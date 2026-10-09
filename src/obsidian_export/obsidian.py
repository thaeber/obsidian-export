import datetime as dt
import logging
import subprocess
from collections.abc import Callable
from pathlib import Path

import psutil
import pydantic

logger = logging.getLogger(__name__)


def is_obsidian_running():
    return any(
        p.info['name'] and p.info['name'].lower() == 'obsidian.exe'
        for p in psutil.process_iter(['name'])
    )


def _decode_command_output(output: bytes | str | None) -> str:
    """Decode subprocess output without relying on the machine's default code page."""
    if output is None:
        return ''
    if isinstance(output, str):
        return output
    return output.decode('utf-8', errors='replace')


def run_obsidian_command(*command: str) -> str | None:
    """Run an Obsidian command using the CLI."""
    try:
        logger.debug(f'Running Obsidian command: obsidian {" ".join(command)}')
        result = subprocess.run(
            ['obsidian', *command],
            capture_output=True,
            check=True,
            shell=False,
        )
        stdout = _decode_command_output(result.stdout)
        logger.debug(f'Command output: {stdout}')
        return stdout
    except FileNotFoundError:
        logger.error('obsidian command not found')
    except subprocess.CalledProcessError as e:
        stderr = _decode_command_output(e.stderr)
        logger.error(f'Command failed with error: {stderr}')


class ObsidianVaultInfo(pydantic.BaseModel):
    name: str
    path: Path
    files: int
    folders: int
    size: int


class ObsidianFileInfo(pydantic.BaseModel):
    path: Path
    name: str
    extension: str
    size: int
    created: dt.datetime
    modified: dt.datetime


def _one_param_per_line_to_dict(
    output: str, conversions: dict[str, Callable[[str], object]] | None = None
) -> dict[str, str]:
    """Convert the output of an Obsidian command that returns one parameter per line to a dictionary."""
    result = {}
    for line in output.strip().split('\n'):
        if '\t' in line:
            key, value = line.split('\t', 1)
            key = key.strip()
            value = value.strip()
            if conversions and key in conversions:
                value = conversions[key](value)
            result[key] = value
    return result


def get_vault_information(vault: str | None = None) -> ObsidianVaultInfo:
    """Get information about an Obsidian vault."""
    cmd = ['vault']
    if vault is not None:
        cmd.append(f'name={vault}')
    vault_info = run_obsidian_command(*cmd)
    if vault_info is None:
        raise RuntimeError(f'Failed to get vault information for {vault}')

    vault_info_dict = _one_param_per_line_to_dict(
        vault_info,
        conversions={
            'path': Path,
            'files': int,
            'folders': int,
            'size': int,
        },
    )
    try:
        return ObsidianVaultInfo.model_validate(vault_info_dict)
    except pydantic.ValidationError as e:
        logger.error(
            f'Could not retrieve vault information for vault: {vault}.'
            ' Possible reasons: the vault does not exist, Obsidian is not'
            ' running, or the Obsidian CLI is not available.'
        )
        raise RuntimeError(f'Failed to get vault information for {vault}') from e


def get_file_information(
    file: Path | str, vault: str | None = None
) -> ObsidianFileInfo:
    """Get information about a file in the Obsidian vault."""
    file = Path(file)
    logger.debug(f'Getting file information for {file} in vault {vault}')
    cmd = ['file']
    if vault is not None:
        cmd.append(f'vault={vault}')
    cmd.append(f'file={file.as_posix()}')
    fino = run_obsidian_command(*cmd)

    if fino is None:
        raise RuntimeError(f'Failed to get file information for {file}')

    to_datetime = lambda x: dt.datetime.fromtimestamp(float(x) / 1000.0).astimezone()

    file_info_dict = _one_param_per_line_to_dict(
        fino,
        conversions={
            'path': Path,
            'size': int,
            'created': to_datetime,
            'modified': to_datetime,
        },
    )
    try:
        return ObsidianFileInfo.model_validate(file_info_dict)
    except pydantic.ValidationError as e:
        logger.error(
            f'Could not retrieve file information for file: {file}.'
            ' Does the file exist in the vault?'
        )
        raise RuntimeError(f'Failed to get file information for {file}') from e


def get_number_of_linked_files(
    file: Path | str,
    vault: str | None = None,
) -> int:
    """Get the number of files linked to a file in the Obsidian vault."""
    file = Path(file)
    cmd = ['links', 'total']
    if vault is not None:
        cmd.append(f'vault={vault}')
    cmd.append(f'file={file.as_posix()}')
    result = run_obsidian_command(*cmd)
    try:
        return int(result.strip())
    except (ValueError, AttributeError):
        logger.error(f'Failed to get number of linked files for {file}')
        return 0


def get_linked_files(
    file: Path | str,
    vault: str | None = None,
    exclude_unresolved: bool = True,
) -> list[str]:
    """Get a list of files linked to a file in the Obsidian vault."""

    # check if there are any linked files first, to avoid running the command if there are none
    num_linked_files = get_number_of_linked_files(file, vault)
    if num_linked_files == 0:
        logger.debug(f'No linked files for {file}')
        return []

    file = Path(file)
    cmd = ['links']
    if vault is not None:
        cmd.append(f'vault={vault}')
    cmd.append(f'file={file.as_posix()}')
    result = run_obsidian_command(*cmd)
    logger.debug(f'Linked files for {file}:\n{result}')
    if result:
        if exclude_unresolved:
            return [
                f.strip() for f in result.strip().split('\n') if not 'unresolved' in f
            ]
        return [f.strip() for f in result.strip().split('\n')]
    return []
