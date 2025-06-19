# import libs
from pathlib import Path
import yaml
from typing import Dict, Union
import re
# locals


def generate_summary(hub: Dict):
    '''
    Generate summary table of the thermodynamic database hub.

    Parameters
    ----------
    hub : dict
        The thermodynamic database hub.
    '''
    try:
        # NOTE: sub items
        items = {}

        for key, value in hub.items():
            # check
            if value:
                items[key] = list(value.keys())

        # NOTE: return summary
        return items
    except Exception as e:
        raise Exception(f"Error in generating summary: {e}") from e


def thermodb_file_loader(
    config_file: Union[Path, str]
) -> Dict:
    '''
    Load thermodynamic database file.

    Parameters
    ----------
    config_file : Path or str
        Path to the thermodynamic database file.

    Returns
    -------
    ref : dict
        Parsed thermodynamic database content as a dictionary.
    '''
    try:
        # check if config_file is Path
        if isinstance(config_file, str):
            config_file = Path(config_file)
        elif not isinstance(config_file, Path):
            raise TypeError("config_file must be a Path or str")

        # NOTE: check if file exists
        if not config_file.is_file():
            raise FileNotFoundError(
                f"Thermodynamic database file {config_file} does not exist.")

        # NOTE: check file extension
        if config_file.suffix.lower() == '.md':
            # load as markdown
            ref = _md_loader(config_file)
        elif config_file.suffix.lower() in ['.yml', '.yaml']:
            # load as yaml
            ref = _yml_loader(config_file)
        elif config_file.suffix.lower() == '.txt':
            # load as txt
            ref = _txt_parser(config_file.read_text())
        else:
            raise ValueError(
                f"Unsupported file format: {config_file.suffix}. "
                "Supported formats are .md, .yml, and .yaml.")

        # return file stem and data
        return ref

    except Exception as e:
        raise Exception(f"Error loading thermodb file: {e}") from e


def _md_loader(config_file: Path) -> dict:
    '''
    Load Markdown content from a file.

    Parameters
    ----------
    config_file : Path
        Path to the Markdown file.

    Returns
    -------
    ref : dict
        Parsed Markdown content as a dictionary.
    '''
    try:
        # check if file exists
        if not config_file.is_file():
            raise FileNotFoundError(
                f"Thermodynamic database file {config_file} does not exist.")

        # load markdown file
        with open(config_file, 'r') as f:
            content = f.read()

        # parse markdown content
        ref = _md_parser(content)

        # return file stem and data
        return ref

    except Exception as e:
        raise ValueError(f"Error parsing Markdown content: {e}") from e


def _yml_loader(config_file: Path) -> dict:
    '''
    Load YAML content from a string.

    Parameters
    ----------
    config_file : Path
        Path to the YAML file.

    Returns
    -------
    ref : dict
        Parsed YAML content as a dictionary.
    '''
    try:
        # check if file exists
        if not config_file.is_file():
            raise FileNotFoundError(
                f"Thermodynamic database file {config_file} does not exist.")

        # load yaml file
        with open(config_file, 'r') as f:
            ref = yaml.safe_load(f)

            # NOTE: check if _ref is None
            if ref is None:
                raise Exception('thermodb rule file is empty!')

        # return file stem and data
        return ref
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML content: {e}") from e


def thermodb_parser(content: str) -> dict:
    '''
    Parse thermodynamic database content.

    Parameters
    ----------
    content : str
        The content of the thermodynamic database.

    Returns
    -------
    dict
        Parsed thermodynamic database.
    '''
    try:
        # NOTE: check if content is empty
        if not content.strip():
            raise ValueError("Content is empty or only whitespace.")

        content = content.strip()

        # SECTION: first try YAML
        try:
            parsed_yaml = yaml.safe_load(content)
            if isinstance(parsed_yaml, dict):
                return parsed_yaml
        except yaml.YAMLError:
            pass  # Not YAML, try markdown next

        # SECTION: Then try Markdown
        if re.search(r"^##\s+\w+", content, re.MULTILINE):
            # yaml pattern
            # parse as yaml
            return _md_parser(content)
        elif re.search(r"^#\s*\S+", content, re.MULTILINE):
            # txt pattern
            # parse as txt
            return _txt_parser(content)
        else:
            # unsupported format
            raise ValueError(
                "Unsupported content format. Expected Markdown or YAML.")
    except Exception as e:
        raise Exception(f"Error parsing thermodb content: {e}") from e


def _yml_parser(content: str):
    '''
    Parse YAML content from a string.

    Parameters
    ----------
    content : str
        The YAML content as a string.
    Returns
    -------
    dict
        Parsed YAML content as a dictionary.
    '''
    try:
        # Parse the YAML content
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML content: {e}") from e
    except Exception as e:
        raise Exception(
            f"Unexpected error while parsing YAML content: {e}") from e


def _md_parser(
    content: str
) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Parse Markdown content to extract thermodynamic data and equations.

    Parameters
    ----------
    content : str
        The Markdown content as a string.

    Returns
    -------
    Dict[str, Dict[str, Dict[str, str]]]
        A dictionary where keys are component names and values are dictionaries
        containing 'DATA' and 'EQUATIONS' sections.
    """
    try:
        # Check if content is empty
        if not content.strip():
            raise ValueError("Content is empty or only whitespace.")

        content = content.strip()

        # Parse the Markdown content
        pattern = re.compile(
            r"^##\s+(?P<component>.+?)\s*?\n"
            r"(?:\s*-\s*DATA:\s*\n(?P<data>(?:\s+.+:.+\n)*))?"
            r"(?:\s*-\s*EQUATIONS:\s*\n(?P<equations>(?:\s+.+:.+\n)*))?",
            re.MULTILINE
        )

        result = {}

        for match in pattern.finditer(content):
            component = match.group("component").strip()
            data_section = match.group("data") or ""
            equations_section = match.group("equations") or ""

            data = {
                key.strip(): value.strip()
                for key, value in re.findall(r"^\s*(.+?):\s*(.+)$", data_section, re.MULTILINE)
            }
            equations = {
                key.strip(): value.strip()
                for key, value in re.findall(r"^\s*(.+?):\s*(.+)$", equations_section, re.MULTILINE)
            }

            result[component] = {
                "DATA": data,
                "EQUATIONS": equations
            }

        return result
    except Exception as e:
        raise ValueError(f"Error parsing Markdown content: {e}") from e


def _txt_parser(
    content: str
) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Parse a plain text thermodynamic config file with sections for each component.

    Parameters
    ----------
    content : str
        The raw content from the .txt file.

    Returns
    -------
    dict
        Parsed dictionary with structure:
        {
            component_name: {
                "DATA": {...},
                "EQUATIONS": {...}
            },
            ...
        }
    """
    try:
        result = {}
        sections = re.split(r"^#\s*(.+)", content, flags=re.MULTILINE)

        # sections[0] is junk before the first match
        for i in range(1, len(sections), 2):
            component = sections[i].strip()
            block = sections[i + 1]

            # Extract DATA and EQUATIONS blocks
            data_block = {}
            equations_block = {}

            data_match = re.search(
                r"-\s*DATA:\s*(.*?)(?=-\s*EQUATIONS:|$)", block, flags=re.DOTALL)
            if data_match:
                data_lines = data_match.group(1).strip().splitlines()
                for line in data_lines:
                    if ':' in line:
                        k, v = map(str.strip, line.split(":", 1))
                        data_block[k] = v

            eq_match = re.search(r"-\s*EQUATIONS:\s*(.*)",
                                 block, flags=re.DOTALL)
            if eq_match:
                eq_lines = eq_match.group(1).strip().splitlines()
                for line in eq_lines:
                    if ':' in line:
                        k, v = map(str.strip, line.split(":", 1))
                        equations_block[k] = v

            result[component] = {
                "DATA": data_block,
                "EQUATIONS": equations_block
            }

        return result
    except Exception as e:
        raise ValueError(f"Error parsing text content: {e}") from e
