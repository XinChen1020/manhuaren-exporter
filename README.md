# Manhuaren Exporter

A small Python script for exporting saved manga data from the SQLite database used by the Manhuaren app.

It was created after locating the app's local SQLite database on macOS and identifying `yq__collect` as the table containing the saved manga collection.

## Features

- Opens the database in **read-only mode**
- Exports `yq__collect` by default
- Supports CSV and JSON
- Can list all SQLite tables
- Can inspect a table's columns
- Uses only Python's standard library

## Requirements

Python 3.9+ is recommended.

No third-party packages are required.

## Usage

Export the saved manga collection to CSV:

```bash
python3 export_manhuaren.py /path/to/database.sqlite
```

This creates:

```text
yq__collect.csv
```

Export as JSON:

```bash
python3 export_manhuaren.py /path/to/database.sqlite --format json
```

Choose an output file:

```bash
python3 export_manhuaren.py /path/to/database.sqlite \
  --output ~/Desktop/manga_collection.csv
```

List available tables:

```bash
python3 export_manhuaren.py /path/to/database.sqlite --list-tables
```

Inspect the saved-manga table:

```bash
python3 export_manhuaren.py /path/to/database.sqlite --describe yq__collect
```

Export another table:

```bash
python3 export_manhuaren.py /path/to/database.sqlite \
  --table yq__read_his \
  --output reading_history.csv
```

## Finding the database on macOS

For the tested app installation, app data was located inside the app's sandbox under its `Data/Library` directory.

A useful way to locate SQLite databases is:

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
- Download mangas through request
- Map manga titles to MyAnimeList IDs
- Generate a MyAnimeList-compatible import file
- Export reading progress and status
