from datetime import date, datetime

from flask import request, render_template, redirect, url_for, abort
from flask import current_app, Blueprint
from flask_babel import format_date

from timebook.models import Timesheet
from timebook import db

BABEL_DEFAULT_DATE_FORMAT = "EEEE d MMMM yyyy"

timesheet_app = Blueprint("timesheet_app", __name__)


@timesheet_app.get("/")
def index():
    """The main page, shows timespan from selected date (or today)."""
    search_date = ensure_valid_date(request.args.get("search_date", ""))
    lines = (
        Timesheet.query.filter_by(day=search_date)
        .order_by(Timesheet.end_time, Timesheet.id)
        .all()
    )
    total_time = sum([t.duration for t in lines])
    total_time = Timesheet.float_time_to_time(total_time)
    return render_template("index.html", search_date=search_date, lines=lines, total_time=total_time)


@timesheet_app.post("/")
def create_timesheet():
    """Submit a new timesheet record for creation."""
    form_data = request.form.to_dict()
    description = form_data.get("description", "/")
    day = ensure_valid_date(form_data.get("search_date", "")).isoformat()
    end_time = form_data.get("end_time", "11:00")
    duration = form_data.get("duration", "00:15")
    new_timesheet = Timesheet(description, day, end_time, duration)
    db.session.add(new_timesheet)
    db.session.commit()
    return redirect(url_for("timesheet_app.index", search_date=new_timesheet.day))


@timesheet_app.get("/edit/<int:time_id>")
def read_timesheet(time_id):
    """Edit page for updating an existing record."""
    record = Timesheet.query.get_or_404(time_id)
    return render_template("edit.html", record=record)


@timesheet_app.post("/edit/<int:time_id>")
def update_timesheet(time_id):
    """Submit an update for an existing record."""
    record = Timesheet.query.get_or_404(time_id)
    form_data = request.form.to_dict()
    if form_data.get("description", False):
        record.description = form_data["description"]
    if form_data.get("day", False):
        record.day = Timesheet.convert_day(form_data["day"])
    if form_data.get("end_time", False):
        record.end_time = Timesheet.time_to_float_time(form_data["end_time"])
    if form_data.get("duration", False):
        record.duration = Timesheet.time_to_float_time(form_data["duration"])
    db.session.commit()
    return redirect(url_for("timesheet_app.index", search_date=record.day))


@timesheet_app.post("/toggle/<int:time_id>")
def toggle_checked(time_id):
    """Alternates `is_checked` status for selected record."""
    record = Timesheet.query.get_or_404(time_id)
    record.is_checked = bool(not record.is_checked)
    db.session.commit()
    return ("", 204)


@timesheet_app.get("/toggle/<int:time_id>")
def toggle_checked_nojs(time_id):
    """Alternates `is_checked` status for selected record. For client without js."""
    res = toggle_checked(time_id)
    return redirect(request.referrer)


@timesheet_app.get("/report")
def report():
    """Print every timesheet recorded in a single page, grouped by day."""
    lines = Timesheet.query.order_by(
        Timesheet.day.desc(), Timesheet.end_time, Timesheet.id
    ).all()
    time_groups = {}
    for record in lines:
        time_key = record.day
        if time_key not in time_groups:
            time_groups[time_key] = [record]
        else:
            time_groups[time_key].append(record)
    return render_template("report.html", time_groups=time_groups)


def ensure_valid_date(input_date: str) -> date:
    """Parse input date, set default if missing, error if invalid."""
    try:
        today_isoformat = date.today().isoformat()
        search_date = date.fromisoformat(input_date or today_isoformat)
    except (ValueError, TypeError) as e:
        current_app.logger.info(e)
        abort(400)  # Bad Request
    return search_date


def pretty_date(value: date) -> str:
    """Date obj into human friendly string."""
    return format_date(value, BABEL_DEFAULT_DATE_FORMAT)
