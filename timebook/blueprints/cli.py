from datetime import date, timedelta

from flask import current_app, Blueprint

import click

from timebook.models import Timesheet
from timebook import db

cli_app = Blueprint('cli', __name__)
cli_app.cli.short_help = 'Command-line interface to manage your Timebook.'


@cli_app.cli.command('time-delete', short_help='Delete a timesheet record.')
@click.argument('time_id')
def time_delete(time_id: int):
    record = Timesheet.query.get_or_404(time_id)
    print_summary(record)
    db.session.delete(record)
    db.session.commit()

@cli_app.cli.command('time-prune', short_help='Remove all archived timesheet records.')
@click.option('--dry-run', is_flag=True, show_default=True, default=False, help='We are living in a simulation.')
def time_prune(dry_run: bool):
    records = Timesheet.query.filter_by(is_checked=True).order_by(Timesheet.day, Timesheet.end_time, Timesheet.id).all()
    for r in records:
        print_summary(r)
    if not dry_run:
        db.session.delete(records)
        db.session.commit()

def print_summary(record: Timesheet):
    """Print a summary text-representation of a timesheet."""
    print('{date} for {duration} from {start_time} to {end_time} "{description}" [id={id}]'.format(
        date=record.day.isoformat(),
        duration=Timesheet.float_time_to_time(record.duration),
        start_time=Timesheet.float_time_to_time(record.get_start_time()),
        end_time=Timesheet.float_time_to_time(record.end_time),
        description=record.description,
        id=record.id
    ))
