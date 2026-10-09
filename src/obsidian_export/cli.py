from __future__ import annotations

import logging
from pathlib import Path

import click
from rich.logging import RichHandler

from obsidian_export.exporter import export_notes

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[RichHandler()],
)


@click.command()
@click.option(
    '--vault',
    default=None,
    help='Name of the Obsidian vault to export. Defaults to the currently open vault if Obsidian.',
)
@click.option(
    '--archive',
    default='.',
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    show_default=True,
    help='Directory to write the archive to. Defaults to the current directory.',
)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debug logging.',
)
@click.argument('root_notes', nargs=-1)
def main(
    vault: str | None, archive: Path, debug: bool, root_notes: tuple[str, ...]
) -> None:
    """Archive notes from an Obsidian vault.

    ROOT_NOTES are the notes in the vault that act as archive roots. Provide
    one or more note paths.
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        export_notes(root_notes, vault, archive)
    except Exception as e:
        raise click.ClickException(f'{e}') from e
