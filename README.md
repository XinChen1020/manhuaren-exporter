# Manhuaren Exporter

A small Python script that exports your saved manga collection from the Manhuaren app's local SQLite database on macOS to CSV or JSON.

Tested only with Manhuaren version **5.2.8** on macOS.

Before running the script, [locate the app's database](#finding-the-database-on-macos) and confirm that it contains `yq__collect`, the default table used to export your saved collection.

## Features

- Opens the database in **read-only mode**
- Exports `yq__collect` by default
- Supports CSV and JSON
- Can list all SQLite tables
- Can inspect a table's columns
- Uses only Python's standard library

## Requirements

Python 3.9 or later is required.

No third-party packages are required.

## Usage

Run the following commands from the repository root. The main script is located at
[`src/manhuaren_exporter/export_manhuaren.py`](src/manhuaren_exporter/export_manhuaren.py).
No package installation is needed.

Export the saved manga collection to CSV:

```bash
python3 src/manhuaren_exporter/export_manhuaren.py /path/to/database.sqlite
```

By default, the export includes every column and creates this file in your current directory:

```text
yq__collect.csv
```

Export as JSON:

```bash
python3 src/manhuaren_exporter/export_manhuaren.py /path/to/database.sqlite --format json
```

Choose an output file:

```bash
python3 src/manhuaren_exporter/export_manhuaren.py /path/to/database.sqlite \
  --output ~/Desktop/manga_collection.csv
```

List available tables:

```bash
python3 src/manhuaren_exporter/export_manhuaren.py /path/to/database.sqlite --list-tables
```

Inspect the saved-manga table:

```bash
python3 src/manhuaren_exporter/export_manhuaren.py /path/to/database.sqlite --describe yq__collect
```

Export another table:

```bash
python3 src/manhuaren_exporter/export_manhuaren.py /path/to/database.sqlite \
  --table yq__read_his \
  --output reading_history.csv
```

## Finding the database on macOS

For the tested app installation, app data was located in the app's sandbox: a dedicated folder under `~/Library/Containers/`. The database was inside that folder's `Data/Library` directory:

```text
~/Library/Containers/<Manhuaren container>/Data/Library/
```

In Finder, press **Command + Shift + G**, enter `~/Library/Containers/`, and locate the Manhuaren container. Open its `Data/Library` directory. The placeholder `<Manhuaren container>` above refers to the app's container folder; its name may be an app identifier rather than “Manhuaren.”

To find the app's bundle identifier, run this in Terminal, replacing the example path with the installed app's actual path:

```bash
mdls -name kMDItemCFBundleIdentifier "/Applications/漫画人极速版.app"
```

You can also type `mdls -name kMDItemCFBundleIdentifier -raw ` (including the trailing space), drag the app from Finder into Terminal to insert its path, and press **Return**. Use the returned identifier to look for the matching folder under `~/Library/Containers/`. If the command returns `(null)`, Spotlight has not provided an identifier for that path.

From the app's `Data/Library` directory, search for SQLite databases with:

```bash
find . -type f -exec file {} \; 2>/dev/null | grep -i sqlite
```

Then inspect a candidate database with:

```bash
sqlite3 /path/to/database.sqlite ".tables"
```

The database used during testing contained tables including:

```text
yq__collect
yq__read_his
yq__downmanga
yq__section
yq__booksection
```

## Future ideas

- Export only useful collection fields instead of every database column
- Download cover images based on links
- Download manga through HTTP requests
- Map manga titles to MyAnimeList IDs
- Generate a MyAnimeList-compatible import file
- Export reading progress and status
