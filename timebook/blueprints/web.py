from datetime import datetime, timedelta

from flask import request, render_template, redirect, url_for
from flask import Blueprint
from sqlalchemy import func

from timebook.utils import ensure_valid_date, ensure_required_fields
from timebook.models import Timespan
from timebook import db

timesheet_app = Blueprint("timesheet_app", __name__)


@timesheet_app.get("/")
def index():
    """The main page, shows timespan from selected date (or today)."""
    search_date = ensure_valid_date(request.args.get("search_date", ""))
    lines = Timespan.query.filter(func.DATE(Timespan.start_at) == search_date)
    lines = lines.order_by(Timespan.start_at, Timespan.id).all()
    total_time = sum([t.duration for t in lines], start=timedelta(0))
    return render_template("index.html", search_date=search_date, lines=lines, total_time=total_time)


@timesheet_app.post("/")
def create_timesheet():
    """Submit a new timesheet record for creation."""
    form_data = ensure_required_fields()
    search_date = ensure_valid_date(form_data.get("search_date", "")).isoformat()
    start_time, end_time = form_data["start_time"], form_data["end_time"]
    start_at = datetime.fromisoformat(f"{search_date}T{start_time}")
    end_at = datetime.fromisoformat(f"{search_date}T{end_time}")
    description = form_data["description"]
    new_timesheet = Timespan(description, start_at, end_at)
    db.session.add(new_timesheet)
    db.session.commit()
    return redirect(url_for("timesheet_app.index", search_date=new_timesheet.start_at.date()))


@timesheet_app.get("/edit/<int:time_id>")
def read_timesheet(time_id):
    """Edit page for updating an existing record."""
    record = Timespan.query.get_or_404(time_id)
    return render_template("edit.html", record=record)


@timesheet_app.post("/edit/<int:time_id>")
def update_timesheet(time_id):
    """Submit an update for an existing record."""
    record: Timespan = Timespan.query.get_or_404(time_id)
    form_data = ensure_required_fields()
    search_date = ensure_valid_date(form_data.get("search_date", "")).isoformat()
    start_time, end_time = form_data["start_time"], form_data["end_time"]
    record.start_at = datetime.fromisoformat(f"{search_date}T{start_time}")
    record.end_at = datetime.fromisoformat(f"{search_date}T{end_time}")
    record.description = form_data["description"]
    db.session.commit()
    return redirect(url_for("timesheet_app.index", search_date=record.start_at.date()))


@timesheet_app.post("/toggle/<int:time_id>")
def toggle_checked(time_id):
    """Alternates `is_archived` status for selected record."""
    record = Timespan.query.get_or_404(time_id)
    record.is_archived = bool(not record.is_archived)
    db.session.commit()
    return ("", 204)


@timesheet_app.get("/toggle/<int:time_id>")
def toggle_checked_nojs(time_id):
    """Alternates `is_archived` status for selected record. For client without js."""
    toggle_checked(time_id)
    return redirect(request.referrer)


@timesheet_app.get("/report")
def report():
    """Print every timesheet recorded in a single page, grouped by day."""
    lines = Timespan.query.order_by(func.DATE(Timespan.start_at).desc(), Timespan.start_at, Timespan.id).all()
    time_groups = {}
    for record in lines:
        time_key = record.start_at.date()
        if time_key not in time_groups:
            time_groups[time_key] = [record]
        else:
            time_groups[time_key].append(record)
    return render_template("report.html", time_groups=time_groups)
