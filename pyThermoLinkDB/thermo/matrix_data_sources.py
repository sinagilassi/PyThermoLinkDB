import logging
from typing import Dict, List, Literal, Optional, cast

from pythermodb_settings.models import Component, Mixture, MixtureKey
from pythermodb_settings.utils import create_mixture_id

from . import Source
from .matrix_data_source import MatrixDataSourceCore


logger = logging.getLogger(__name__)


class MatrixDataSourcesCore:
    """
    Core adapter for building matrix data sources for multiple mixtures.

    This class mirrors the multi-source role of ``EquationSourcesCore`` for
    equation sources, but it operates at the mixture level. Each mixture is
    represented by a list of ``Component`` objects and is resolved to a stable
    mixture id before a ``MatrixDataSourceCore`` is built for it.
    """

    def __init__(
        self,
        mixture_components: List[Mixture],
        source: Source,
        mixture_key: MixtureKey = 'Name',
        extract_list: Optional[list[str]] = None,
        check_build: bool = False,
        delimiter: str = '|',
        case: Literal['lower', 'upper'] | None = None,
    ) -> None:
        """
        Initialize matrix data sources for multiple mixtures.

        Parameters
        ----------
        mixture_components : List[Mixture]
            List of mixtures, where each mixture is a non-empty list of
            ``Component`` objects.
        source : Source
            Source containing matrix data.
        mixture_key : MixtureKey
            Key used to build mixture ids. Defaults to ``'Name'``.
        extract_list : Optional[list[str]]
            Matrix properties to retain for every mixture. ``None`` means all
            available properties.
        check_build : bool
            Whether to log build failures after each mixture source is built.
        delimiter : str
            Delimiter used in generated mixture ids.
        case : Literal['lower', 'upper'] | None
            Optional case normalization for generated mixture ids.
        """
        self.mixture_components = mixture_components
        self.source = source
        self.mixture_key = mixture_key
        self.extract_list = extract_list
        self.check_build = check_build
        self.delimiter = delimiter
        self.case = case

        self.mixture_ids: List[str] = self._build_mixture_ids()
        self._src: Dict[str, MatrixDataSourceCore] = self.build()

    @property
    def src(self) -> Dict[str, MatrixDataSourceCore]:
        """
        Get all built matrix data sources keyed by mixture id.

        Returns
        -------
        Dict[str, MatrixDataSourceCore]
            Matrix data sources for each requested mixture.
        """
        return self._src

    def _build_mixture_ids(self) -> List[str]:
        """
        Build mixture ids for all configured mixtures.

        Returns
        -------
        List[str]
            Generated mixture ids in the same order as ``mixture_components``.
        """
        mixture_ids: List[str] = []

        for components in self.mixture_components:
            mixture_ids.append(
                create_mixture_id(
                    components=components,
                    mixture_key=cast(MixtureKey, self.mixture_key),
                    delimiter=self.delimiter,
                    case=cast(Literal['lower', 'upper'], self.case),
                )
            )

        return mixture_ids

    def summary(self) -> Dict[str, Dict[str, bool]]:
        """
        Report extraction status for every mixture.

        Returns
        -------
        Dict[str, Dict[str, bool]]
            Mapping of mixture id to the corresponding
            ``MatrixDataSourceCore.summary()`` result.
        """
        return {
            mixture_id: matrix_source.summary()
            for mixture_id, matrix_source in self._src.items()
        }

    def build_status(self) -> bool:
        """
        Return whether every requested matrix property was built for every mixture.

        Returns
        -------
        bool
            ``True`` when all mixture sources report a successful build.
        """
        return all(
            matrix_source.build_status()
            for matrix_source in self._src.values()
        )

    def build(self) -> Dict[str, MatrixDataSourceCore]:
        """
        Build matrix data sources for all configured mixtures.

        Returns
        -------
        Dict[str, MatrixDataSourceCore]
            Matrix data sources keyed by generated mixture id.
        """
        try:
            matrix_sources: Dict[str, MatrixDataSourceCore] = {}

            for components, mixture_id in zip(
                self.mixture_components,
                self.mixture_ids,
            ):
                matrix_source = MatrixDataSourceCore(
                    components=components,
                    source=self.source,
                    mixture_key=cast(MixtureKey, self.mixture_key),
                    extract_list=self.extract_list,
                    delimiter=self.delimiter,
                    case=cast(Literal['lower', 'upper'] | None, self.case),
                )

                if self.check_build and not matrix_source.build_status():
                    logger.error(
                        "Failed to build matrix data source for mixture "
                        f"'{mixture_id}'. Build summary: {matrix_source.summary()}"
                    )

                matrix_sources[mixture_id] = matrix_source

            return matrix_sources
        except Exception as e:
            logger.error(f"Error creating matrix data sources: {e}")
            return {}

    def select(
        self,
        mixture_id: str,
    ) -> Optional[MatrixDataSourceCore]:
        """
        Select a built matrix data source by mixture id.

        Parameters
        ----------
        mixture_id : str
            Mixture id generated from ``mixture_components``.

        Returns
        -------
        Optional[MatrixDataSourceCore]
            The selected matrix data source, or ``None`` when missing.
        """
        try:
            matrix_source = self._src.get(mixture_id)

            if matrix_source is None:
                logger.error(
                    f"Matrix data source for mixture '{mixture_id}' not found."
                )
                return None

            return matrix_source
        except Exception as e:
            logger.error(f"Error selecting matrix data source: {e}")
            return None
