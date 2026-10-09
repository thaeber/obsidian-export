# Obsidian Export

Export one or more Obsidian notes and all of their linked content into a local archive directory.

This project is designed for creating a portable snapshot of a note tree from an Obsidian vault, including the referenced notes and files that are discovered through Obsidian's own link graph.

## Features

- Exports a root note or multiple root notes from an Obsidian vault
- Recursively follows linked files and copies them to an archive directory
- Preserves the original vault-relative folder structure under the archive
- Uses the Obsidian CLI to inspect vaults, files, and linked resources
- Outputs progress information with Rich while exporting

## Requirements

- Python 3.14+
- An Obsidian vault installed on the machine
- The `obsidian` command available on your `PATH`
- Obsidian's local CLI enabled in the app

The project relies on Obsidian's command-line interface to enumerate vault state and linked files.

To enable the CLI in Obsidian itself on the latest version:

1. Open Obsidian.
2. Go to Settings.
3. Open the General section.
4. Enable the option that activates the Obsidian command-line interface / local CLI support.
5. Restart Obsidian if prompted, then verify `obsidian --help` works in a terminal.

This is the current setup path in newer Obsidian releases, and it is required for the native `obsidian` command used by this project to be available on your system.

Official Obsidian documentation: https://help.obsidian.md/advanced/command-line-interface

## Installation

Install the CLI as a `uv` tool:

```bash
uv tool install --editable .
```

This installs the `obsidian-export` command into your `uv` tool environment and makes it available from the terminal.

To confirm the CLI is available:

```bash
obsidian-export --help
```

## Usage

After installation, the CLI entry point is:

```bash
obsidian-export --help
```

### Export a single note

```bash
obsidian-export --vault "My Vault" --archive ./archive "Projects/Project A"
```

### Export multiple root notes

```bash
obsidian-export --vault "My Vault" --archive ./archive "Projects/Project A" "Projects/Project B"
```

### Use the current vault automatically

```bash
obsidian-export --archive ./archive "Projects/Project A"
```

### Debug output

```bash
obsidian-export --debug --vault "My Vault" --archive ./archive "Projects/Project A"
```

## How it works

The exporter:

1. Resolves the target Obsidian vault.
2. Reads the root note(s) you provide.
3. Collects all files linked from those notes.
4. Copies each file into the archive directory under the same relative path structure.
5. Continues until all linked files have been exported.

This makes it useful for archiving a knowledge base subtree or preparing a note collection for backup, sharing, or external processing.

## Example directory layout

```text
archive/
└── Projects/
    └── Project A.md
        ...
```

The exact structure depends on the files and links inside the selected Obsidian content.

## Notes

- `root_notes` are the vault-relative note paths to treat as export roots.
- Files that are unresolved or not available in the vault are skipped when Obsidian reports them as such.
- The exported archive is intended as a copied snapshot, not a live sync with the vault.

## Development

```bash
uv sync
uv run pytest
```

## License

This project does not currently declare a license in the package metadata. Check the repository for the licensing status before redistributing or publishing the project.
