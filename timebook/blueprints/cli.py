from flask import Blueprint

import click

from timebook.models import Timespan
from timebook import db

cli_app = Blueprint("cli", __name__)
cli_app.cli.short_help = "Command-line interface to manage your Timebook."


@cli_app.cli.command("time-delete", short_help="Delete a timesheet record.")
@click.argument("time_id")
def time_delete(time_id: int):
    record = Timespan.query.get_or_404(time_id)
    print(record.to_string())
    db.session.delete(record)
    db.session.commit()


@cli_app.cli.command("time-prune", short_help="Remove all archived timesheet records.")
@click.option("-y", "--yes", is_flag=True, default=False, help="Confirm cleanup, default behavior is dry-run mode.")
def time_prune(yes: bool):
    archived = Timespan.query.filter_by(is_archived=True)
    for record in archived.order_by(Timespan.start_at, Timespan.id).all():
        print(record.to_string())
    if yes:
        archived.delete(synchronize_session=False)
        db.session.commit()
