# Timebook
Simple web application for tracking how you spend your time,
slightly inspired by Traggo (a great open source tag-based time-tracking tool)
but without tags.

![](.github/screenshot.png)


## Features
- Time-tracking based on free text description, start time and end time.
- List timespans by date, or show all.
- Generic "archived" status, to mark already reported/invoiced/whatever records.
- Light and dark themes.


## Docker
The recommended way to run Timebook is using Docker and Docker Compose.

| Environment variable | Description |
|----------------------|-------------|
| `TIMEBOOK_DATABASE_URI` | Database connection string (default: `sqlite:///time.db`) |
| `TIMEBOOK_LOCALE` | Locale for date/time formatting (default: `en`) |
| `TIMEBOOK_SECRET_KEY` | Secret key for sessions |

If you want to keep the default SQLite database, remember to mount `/app/instance`
as a persistent volume so the database file stays on the host in case
the container is recreated.


## Running locally
Timebook requires Python 3.8 or newer and a database
(SQLite by default or other engines like PostgreSQL).

Create a virtual environment and install dependencies with

    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt

Then run the development server with

    flask run --debug

Or the production server with

    gunicorn


## Command-line interface
A command-line interface (CLI) is available for managing time records.

    flask timectl --help
    flask timectl list 2023-04-03
    flask timectl add  # interactive or with options
    flask timectl edit 3 --end "15:30"
    flask timectl delete 5
    flask timectl prune --yes


## Credits
CSS style based on [ajusa/lit](https://github.com/ajusa/lit),
a ridiculously small responsive css framework.
