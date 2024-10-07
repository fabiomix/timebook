from datetime import date, datetime

import click

from flask import Blueprint
from sqlalchemy import func

from timebook.models import Timespan
from timebook import db

cli_app = Blueprint("timectl", __name__)
cli_app.cli.short_help = "Command-line interface to manage your Timebook."


@cli_app.cli.command("list", short_help="List timespans for a given date.")
@click.argument("search_date")
def time_list(search_date: str):
    """List all Timespan records for the given date."""
    try:
        filter_date = date.fromisoformat(search_date)
    except Exception:
        raise click.BadParameter("Invalid date format. Use YYYY-MM-DD")

    results = Timespan.query.filter(func.DATE(Timespan.start_at) == filter_date)
    results = results.order_by(Timespan.start_at, Timespan.id).all()

    if not results:
        print(f"No records for {search_date}")
        return

    for rec in results:
        print(rec.to_string())


@cli_app.cli.command("add", short_help="Add a new timespan record.")
@click.option("-t", "--title", default=None, help="Set description.")
@click.option("-d", "--day", default=None, help="Set date (YYYY-MM-DD).")
@click.option("-s", "--start", default=None, help="Set start time (HH:MM).")
@click.option("-e", "--end", default=None, help="Set end time (HH:MM).")
def time_add(title: str, day: str, start: str, end: str):
    """Add a new timespan record."""

    if title is None:
        title = click.prompt("Description", show_default=False)
    if day is None:
        day = click.prompt("Date (YYYY-MM-DD)", default=date.today().isoformat(), show_default=True)
    if start is None:
        start = click.prompt("Start Time (HH:MM)", show_default=False)
    if end is None:
        end = click.prompt("End Time (HH:MM)", show_default=False)

    try:
        start_at = datetime.fromisoformat(f"{day} {start}")
        end_at = datetime.fromisoformat(f"{day} {end}")
    except Exception:
        raise click.BadParameter("Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time.")

    new_record = Timespan(title, start_at, end_at)
    db.session.add(new_record)
    db.session.commit()


@cli_app.cli.command("edit", short_help="Edit a timespan record.")
@click.argument("time_id")
@click.option("-t", "--title", default=None, help="New description.")
@click.option("-d", "--day", default=None, help="New date (YYYY-MM-DD).")
@click.option("-s", "--start", default=None, help="New start time (HH:MM).")
@click.option("-e", "--end", default=None, help="New end time (HH:MM).")
@click.option("--archive/--restore", default=None, help="Set the archived flag.")
def time_edit(time_id: int, title: str, day: str, start: str, end: str, archive: bool):
    """Edit a timespan record. Leave prompts empty to keep the current value."""
    record = Timespan.query.get_or_404(time_id)

    def _parse_dt(new_date: str, new_time: str, current: datetime) -> datetime:
        if new_date is None or new_time is None:
            return current
        try:
            return datetime.fromisoformat(f"{new_date} {new_time}")
        except Exception:
            raise Exception("Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time.")

    # If any option is provided, use only options - else prompt all
    if any([title, day, start, end, archive is not None]):
        description = title if title is not None else record.description
        search_date = day if day is not None else record.start_at.date().isoformat()
        start_time = start if start is not None else record.start_at.time().isoformat(timespec="minutes")
        end_time = end if end is not None else record.end_at.time().isoformat(timespec="minutes")
        is_archived = archive if archive is not None else record.is_archived

    else:
        description = click.prompt("Description", default=record.description, show_default=True)
        search_date = click.prompt("Date (YYYY-MM-DD)", default=record.start_at.date().isoformat(), show_default=True)
        start_time = click.prompt("Start Time (HH:MM)", default=record.start_at.time().isoformat(timespec="minutes"), show_default=True)
        end_time = click.prompt("End Time (HH:MM)", default=record.end_at.time().isoformat(timespec="minutes"), show_default=True)
        is_archived = click.confirm("Is archived?", default=record.is_archived)

    start_at = _parse_dt(search_date, start_time, record.start_at)
    end_at = _parse_dt(search_date, end_time, record.end_at)
    record.description = description
    record.start_at = start_at
    record.end_at = end_at
    record.is_archived = is_archived
    db.session.commit()


@cli_app.cli.command("delete", short_help="Delete a timespan record.")
@click.argument("time_id")
def time_delete(time_id: int):
    record = Timespan.query.get_or_404(time_id)
    print(record.to_string())
    db.session.delete(record)
    db.session.commit()


@cli_app.cli.command("prune", short_help="Remove all archived timespan records.")
@click.option("-y", "--yes", is_flag=True, default=False, help="Confirm cleanup, default behavior is dry-run mode.")
def time_prune(yes: bool):
    archived = Timespan.query.filter_by(is_archived=True)
    for record in archived.order_by(Timespan.start_at, Timespan.id).all():
        print(record.to_string())
    if yes:
        archived.delete(synchronize_session=False)
        db.session.commit()
