import logging
import shutil
from collections.abc import Iterable
from pathlib import Path

from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from .obsidian import get_file_information, get_linked_files, get_vault_information


def export_notes(
    notes: Iterable[str], vault: str | None, archive: Path = Path('.')
) -> None:
    """Archive notes from an Obsidian vault.

    ROOT_NOTES are the notes in the vault that act as archive roots. Provide
    one or more note paths.
    """
    logger = logging.getLogger(__name__)

    # get vault information
    vault_info = get_vault_information(vault)

    # build initial list of files to export, starting with the root notes
    files_to_export = [get_file_information(note, vault) for note in notes]
    processed: list[Path] = []

    progress = Progress(
        TextColumn('[bold blue]{task.description}'),
        BarColumn(bar_width=None),
        TaskProgressColumn(),  # percentage
        TextColumn('{task.completed}/{task.total}'),
        TimeElapsedColumn(),
        expand=True,
    )

    with progress:
        task = progress.add_task(
            '[green]Exporting notes...', total=len(files_to_export)
        )
        while files_to_export:
            file = files_to_export.pop()
            if file.path in processed:
                continue

            # copy file to archive directory
            logger.info(f'Exporting {file.path}')
            archive_path = archive / file.path
            if not archive_path.parent.exists():
                archive_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(vault_info.path / file.path, archive_path)

            # add any linked files to the list of files to export
            linked_files = get_linked_files(file.path, vault)
            logger.info(f'Found {len(linked_files)} linked files for {file.path}')
            if linked_files:
                for linked_file in linked_files:
                    linked_file_info = get_file_information(linked_file, vault)
                    if linked_file_info.path not in processed:
                        files_to_export.append(linked_file_info)
                        progress.update(task, total=progress.tasks[0].total + 1)  # type: ignore

            processed.append(file.path)
            progress.update(task, advance=1)
