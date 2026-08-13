"""Validation for built thermodynamic source mappings."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

THERMO_SRC_KEYS = ("src", "comp", "value", "eq", "mode")


# SECTION: Validation result data structures
@dataclass
class ValidationIssue:
    """Single validation issue found in a built thermo source."""

    level: str
    code: str
    message: str
    symbol: Optional[str] = None
    component_id: Optional[str] = None


@dataclass
class ValidationReport:
    """Validation details for a built thermo source."""

    issues: List[ValidationIssue] = field(default_factory=list)
    missing_requested: List[str] = field(default_factory=list)
    missing_data: Dict[str, List[str]] = field(default_factory=dict)
    missing_equations: Dict[str, List[str]] = field(default_factory=dict)
    missing_mixtures: Dict[str, List[str]] = field(default_factory=dict)
    missing_matrix_data: List[str] = field(default_factory=list)
    missing_constants: List[str] = field(default_factory=list)

    # NOTE: These properties expose common report status checks without
    # requiring callers to inspect the raw issue and missing-data collections.
    @property
    def is_valid(self) -> bool:
        """Return ``True`` when no error-level issues were found."""
        return not any(issue.level == "error" for issue in self.issues)

    @property
    def all_requested_available(self) -> bool:
        """Return ``True`` when all requested symbols have usable entries."""
        return (
            not self.missing_requested
            and not self.missing_data
            and not self.missing_equations
            and not self.missing_mixtures
            and not self.missing_matrix_data
            and not self.missing_constants
        )

    @property
    def all_components_available(self) -> bool:
        """Return ``True`` when component-wise data/equations cover all components."""
        return not self.missing_data and not self.missing_equations

    @property
    def all_mixtures_available(self) -> bool:
        """Return ``True`` when mixture-keyed matrix data covers all mixtures."""
        return not self.missing_mixtures and not self.missing_matrix_data

    @property
    def errors(self) -> List[ValidationIssue]:
        """Return error-level issues."""
        return [issue for issue in self.issues if issue.level == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        """Return warning-level issues."""
        return [issue for issue in self.issues if issue.level == "warning"]

    def add_issue(
            self,
            level: str,
            code: str,
            message: str,
            symbol: Optional[str] = None,
            component_id: Optional[str] = None,
    ) -> None:
        """Add one issue to the report."""
        self.issues.append(
            ValidationIssue(
                level=level,
                code=code,
                message=message,
                symbol=symbol,
                component_id=component_id,
            )
        )

    def summary(self) -> Dict[str, Any]:
        """Return a compact validation summary."""
        return {
            "is_valid": self.is_valid,
            "all_requested_available": self.all_requested_available,
            "all_components_available": self.all_components_available,
            "all_mixtures_available": self.all_mixtures_available,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "missing_requested": self.missing_requested,
            "missing_data": self.missing_data,
            "missing_equations": self.missing_equations,
            "missing_mixtures": self.missing_mixtures,
            "missing_matrix_data": self.missing_matrix_data,
            "missing_constants": self.missing_constants,
        }


class ThermoSourceValidator:
    """
    Validate one built ``thermo_src`` mapping without raising.

    The source object must expose ``thermo_src`` and may expose
    ``requested_data``, ``requested_equations``, ``requested_constants``, and
    ``component_references``.
    """

    def __init__(
            self,
            source: Any,
            component_ids: Optional[List[str]] = None,
    ) -> None:
        """Store source context and initialize an empty validation report."""
        self.source = source
        self.component_ids = component_ids
        self.report = ValidationReport()

    # SECTION: Main validation workflow
    def validate(self) -> Optional[ValidationReport]:
        """Run source validation and return a report, or ``None`` on failure."""
        try:
            thermo_src = self._thermo_src()
            if thermo_src is None:
                logger.error("Thermo source does not expose a valid thermo_src dictionary.")
                return None

            self.report = ValidationReport()
            checks = (
                self.validate_source_shape,
                self.validate_requested_symbols,
                self.validate_data_availability,
                self.validate_equation_availability,
                self.validate_matrix_data_availability,
                self.validate_constant_availability,
                self.validate_component_alignment,
                self.validate_numeric_values,
            )

            for check in checks:
                if check() is None:
                    return None

            return self.report
        except Exception as exc:
            logger.error(f"Thermo source validation failed: {exc}")
            return None

    # SECTION: Public validation checks
    def validate_source_shape(self) -> Optional[ValidationReport]:
        """Check each symbol entry has the canonical fixed keys."""
        try:
            thermo_src = self._thermo_src() or {}
            if not thermo_src:
                self._add_warning("empty_thermo_src", "Thermo source is empty.")
                return self.report

            for symbol, entry in thermo_src.items():
                if not isinstance(entry, dict):
                    self._add_error(
                        "invalid_symbol_entry",
                        f"Thermo source entry for '{symbol}' is not a dictionary.",
                        symbol=symbol,
                    )
                    continue

                missing_keys = [
                    key for key in THERMO_SRC_KEYS if key not in entry
                ]
                if missing_keys:
                    self._add_error(
                        "missing_entry_keys",
                        f"Thermo source entry for '{symbol}' is missing keys: {missing_keys}.",
                        symbol=symbol,
                    )

            return self.report
        except Exception as exc:
            logger.error(f"Source-shape validation failed: {exc}")
            return None

    def validate_requested_symbols(self) -> Optional[ValidationReport]:
        """Check all requested symbols are present in ``thermo_src``."""
        try:
            thermo_src = self._thermo_src() or {}
            requested_symbols = [
                *self._requested("requested_data"),
                *self._requested("requested_equations"),
                *self._requested("requested_matrix_data"),
                *self._requested("requested_constants"),
            ]

            for symbol in dict.fromkeys(requested_symbols):
                if symbol not in thermo_src:
                    self._record_missing_requested(symbol)

            return self.report
        except Exception as exc:
            logger.error(f"Requested-symbol validation failed: {exc}")
            return None

    def validate_data_availability(self) -> Optional[ValidationReport]:
        """Check requested data has source, component values, and values."""
        try:
            thermo_src = self._thermo_src() or {}
            component_ids = self._component_ids()

            for symbol in self._requested("requested_data"):
                entry = thermo_src.get(symbol)
                if not isinstance(entry, dict):
                    continue

                self._check_present(entry, "src", "missing_data_source", symbol)
                self._check_present(entry, "comp", "missing_data_components", symbol)
                self._check_present(entry, "value", "missing_data_value", symbol)

                comp = entry.get("comp")
                if isinstance(comp, dict):
                    for component_id in component_ids:
                        if component_id not in comp:
                            self._record_missing_component(
                                self.report.missing_data,
                                "missing_component_data",
                                (
                                    f"Data source for symbol '{symbol}' is missing "
                                    f"component '{component_id}'."
                                ),
                                symbol,
                                component_id,
                            )

            return self.report
        except Exception as exc:
            logger.error(f"Data-availability validation failed: {exc}")
            return None

    def validate_equation_availability(self) -> Optional[ValidationReport]:
        """Check requested equations have equation sources for all components."""
        try:
            thermo_src = self._thermo_src() or {}
            component_ids = self._component_ids()

            for symbol in self._requested("requested_equations"):
                entry = thermo_src.get(symbol)
                if not isinstance(entry, dict):
                    continue

                self._check_present(entry, "eq", "missing_equation_source", symbol)

                eq = entry.get("eq")
                if isinstance(eq, dict):
                    for component_id in component_ids:
                        if component_id not in eq:
                            self._record_missing_component(
                                self.report.missing_equations,
                                "missing_component_equation",
                                (
                                    f"Equation source for symbol '{symbol}' is missing "
                                    f"component '{component_id}'."
                                ),
                                symbol,
                                component_id,
                            )

            return self.report
        except Exception as exc:
            logger.error(f"Equation-availability validation failed: {exc}")
            return None

    def validate_matrix_data_availability(self) -> Optional[ValidationReport]:
        """Check requested matrix data has source entries."""
        try:
            thermo_src = self._thermo_src() or {}
            mixture_ids = self._mixture_ids()

            for symbol in self._requested("requested_matrix_data"):
                entry = thermo_src.get(symbol)
                if not isinstance(entry, dict):
                    self._record_missing_matrix_data(symbol)
                    continue

                if self._is_empty(entry.get("src")):
                    self._record_missing_matrix_data(symbol)
                    self._add_error(
                        "missing_matrix_data_source",
                        f"Matrix data source for '{symbol}' is missing.",
                        symbol=symbol,
                    )

                    continue

                src = entry.get("src")
                if isinstance(src, dict) and mixture_ids:
                    for mixture_id in mixture_ids:
                        if mixture_id not in src:
                            self._record_missing_mixture(
                                "missing_mixture_matrix_data",
                                (
                                    f"Matrix data source for symbol '{symbol}' "
                                    f"is missing mixture '{mixture_id}'."
                                ),
                                symbol,
                                mixture_id,
                            )

            return self.report
        except Exception as exc:
            logger.error(f"Matrix-data availability validation failed: {exc}")
            return None

    def validate_constant_availability(self) -> Optional[ValidationReport]:
        """Check requested constants have source and value entries."""
        try:
            thermo_src = self._thermo_src() or {}

            for symbol in self._requested("requested_constants"):
                entry = thermo_src.get(symbol)
                if not isinstance(entry, dict):
                    self._record_missing_constant(symbol)
                    continue

                if self._is_empty(entry.get("src")):
                    self._record_missing_constant(symbol)
                    self._add_error(
                        "missing_constant_source",
                        f"Constant source for '{symbol}' is missing.",
                        symbol=symbol,
                    )

                if self._is_empty(entry.get("value")):
                    self._add_error(
                        "missing_constant_value",
                        f"Constant value for '{symbol}' is missing.",
                        symbol=symbol,
                    )

            return self.report
        except Exception as exc:
            logger.error(f"Constant-availability validation failed: {exc}")
            return None

    def validate_component_alignment(self) -> Optional[ValidationReport]:
        """Check component dictionaries and value arrays have matching lengths."""
        try:
            thermo_src = self._thermo_src() or {}
            for symbol, entry in thermo_src.items():
                if not isinstance(entry, dict):
                    continue

                comp = entry.get("comp")
                value = entry.get("value")
                if not isinstance(comp, dict) or self._is_empty(comp):
                    continue

                value_length = self._value_length(value)
                if value_length is not None and value_length != len(comp):
                    self._add_error(
                        "component_value_length_mismatch",
                        (
                            f"Value length for '{symbol}' is {value_length}, "
                            f"but component mapping length is {len(comp)}."
                        ),
                        symbol=symbol,
                    )

            return self.report
        except Exception as exc:
            logger.error(f"Component-alignment validation failed: {exc}")
            return None

    def validate_numeric_values(self) -> Optional[ValidationReport]:
        """Check component-wise values are finite numbers."""
        try:
            thermo_src = self._thermo_src() or {}
            for symbol, entry in thermo_src.items():
                if not isinstance(entry, dict):
                    continue

                comp = entry.get("comp")
                if not isinstance(comp, dict):
                    continue

                for component_id, value in comp.items():
                    if not self._is_finite_number(value):
                        self._add_error(
                            "invalid_component_value",
                            (
                                f"Component value for '{symbol}' and "
                                f"'{component_id}' is not finite numeric."
                            ),
                            symbol=symbol,
                            component_id=component_id,
                        )

            return self.report
        except Exception as exc:
            logger.error(f"Numeric-value validation failed: {exc}")
            return None

    def summary(self) -> Dict[str, Any]:
        """Return a compact summary for the last validation run."""
        return self.report.summary()

    # SECTION: Source metadata helpers
    def _thermo_src(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """Return the source ``thermo_src`` mapping when it has dict shape."""
        thermo_src = getattr(self.source, "thermo_src", None)
        if isinstance(thermo_src, dict):
            return thermo_src
        return None

    def _requested(self, attr: str) -> List[str]:
        """Return requested symbol names from a source attribute as a list."""
        requested = getattr(self.source, attr, [])
        if requested is None:
            return []
        return list(requested)

    def _component_ids(self) -> List[str]:
        """Return explicit or source-provided component identifiers."""
        if self.component_ids is not None:
            return self.component_ids

        component_references = getattr(self.source, "component_references", {})
        if isinstance(component_references, dict):
            component_ids = component_references.get("component_ids", [])
            if isinstance(component_ids, list):
                return component_ids

        return []

    def _mixture_ids(self) -> List[str]:
        """Return mixture identifiers from source metadata as a list."""
        mixture_references = getattr(self.source, "mixture_references", {})
        if isinstance(mixture_references, dict):
            mixture_ids = (
                mixture_references.get("mixture_ids")
                or mixture_references.get("mixture_id")
                or []
            )
            if isinstance(mixture_ids, str):
                return [mixture_ids]
            if isinstance(mixture_ids, list):
                return mixture_ids

        return []

    # SECTION: Missing-field and missing-symbol recorders
    def _check_present(
            self,
            entry: Dict[str, Any],
            key: str,
            code: str,
            symbol: str,
    ) -> None:
        """Add an error when a required entry field is empty or absent."""
        if self._is_empty(entry.get(key)):
            self._add_error(
                code,
                f"Thermo source field '{key}' for '{symbol}' is missing.",
                symbol=symbol,
            )

    def _record_missing_requested(self, symbol: str) -> None:
        """Record a requested symbol that has no ``thermo_src`` entry."""
        if symbol not in self.report.missing_requested:
            self.report.missing_requested.append(symbol)
        self._add_error(
            "missing_requested_symbol",
            f"Requested symbol '{symbol}' is missing from thermo_src.",
            symbol=symbol,
        )

    def _record_missing_component(
            self,
            missing: Dict[str, List[str]],
            code: str,
            message: str,
            symbol: str,
            component_id: str,
    ) -> None:
        """Record a missing component for data or equation availability."""
        missing.setdefault(symbol, [])
        if component_id not in missing[symbol]:
            missing[symbol].append(component_id)
        self._add_error(
            code,
            message,
            symbol=symbol,
            component_id=component_id,
        )

    def _record_missing_mixture(
            self,
            code: str,
            message: str,
            symbol: str,
            mixture_id: str,
    ) -> None:
        """Record a missing mixture-specific matrix-data source."""
        self.report.missing_mixtures.setdefault(symbol, [])
        if mixture_id not in self.report.missing_mixtures[symbol]:
            self.report.missing_mixtures[symbol].append(mixture_id)
        self._add_error(
            code,
            message,
            symbol=symbol,
            component_id=mixture_id,
        )

    def _record_missing_constant(self, symbol: str) -> None:
        """Record a requested constant whose source entry is unusable."""
        if symbol not in self.report.missing_constants:
            self.report.missing_constants.append(symbol)

    def _record_missing_matrix_data(self, symbol: str) -> None:
        """Record requested matrix data whose source entry is unusable."""
        if symbol not in self.report.missing_matrix_data:
            self.report.missing_matrix_data.append(symbol)

    # SECTION: Issue logging helpers
    def _add_error(
            self,
            code: str,
            message: str,
            symbol: Optional[str] = None,
            component_id: Optional[str] = None,
    ) -> None:
        """Log and append one error-level validation issue."""
        logger.error(message)
        self.report.add_issue(
            level="error",
            code=code,
            message=message,
            symbol=symbol,
            component_id=component_id,
        )

    def _add_warning(
            self,
            code: str,
            message: str,
            symbol: Optional[str] = None,
            component_id: Optional[str] = None,
    ) -> None:
        """Log and append one warning-level validation issue."""
        logger.warning(message)
        self.report.add_issue(
            level="warning",
            code=code,
            message=message,
            symbol=symbol,
            component_id=component_id,
        )

    # SECTION: Value-shape and numeric helpers
    def _is_empty(self, value: Any) -> bool:
        """Return ``True`` when a supported value container has no content."""
        if value is None:
            return True
        if isinstance(value, np.ndarray):
            return value.size == 0
        if isinstance(value, (dict, list, tuple, set, str)):
            return len(value) == 0
        return False

    def _value_length(self, value: Any) -> Optional[int]:
        """Return the length of array-like values, or ``None`` if scalar/unknown."""
        if value is None:
            return None
        if isinstance(value, np.ndarray):
            return int(value.size)
        if isinstance(value, (list, tuple)):
            return len(value)
        return None

    def _is_finite_number(self, value: Any) -> bool:
        """Return ``True`` only for non-boolean finite numeric values."""
        if isinstance(value, bool):
            return False
        if not isinstance(value, (int, float, np.number)):
            return False
        return math.isfinite(float(value))
