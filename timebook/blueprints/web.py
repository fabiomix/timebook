from datetime import date, datetime, timedelta

from flask import abort, Blueprint, current_app, redirect, render_template, request, url_for
from sqlalchemy import func

from timebook.forms import TimespanCreateForm, TimespanDeleteForm, TimespanEditForm
from timebook.models import Timespan
from timebook import csrf, db

web_app = Blueprint("web_app", __name__)


@web_app.route("/health")
def health():
    return "OK", 200


@web_app.route("/", methods=["GET", "POST"])
def index():
    form = TimespanCreateForm()

    if request.method == "POST":
        if form.validate_on_submit():
            search_date = form.search_date.data
            start_at = datetime.combine(search_date, form.start_time.data)  # type: ignore
            end_at = datetime.combine(search_date, form.end_time.data)  # type: ignore
            new_record = Timespan(form.description.data, start_at, end_at)  # type: ignore
            db.session.add(new_record)
            db.session.commit()
            return redirect(url_for("web_app.index", search_date=search_date))
        else:
            current_app.logger.error(f"Form validation failed: {form.errors}")
            abort(400)  # Bad Request

    search_date = request.args.get("search_date", date.today().isoformat())
    search_date = date.fromisoformat(search_date)
    lines = Timespan.query.filter(func.DATE(Timespan.start_at) == search_date)
    lines = lines.order_by(Timespan.start_at, Timespan.id).all()
    total_time = sum([t.duration for t in lines], start=timedelta(0))
    return render_template("index.html", form=form, search_date=search_date, lines=lines, total_time=total_time)


@web_app.route("/edit/<int:time_id>", methods=["GET", "POST"])
def edit(time_id):
    record = Timespan.query.get_or_404(time_id)
    form = TimespanEditForm(obj=record)

    if request.method == "POST":
        if form.validate_on_submit():
            search_date = form.search_date.data
            record.start_at = datetime.combine(search_date, form.start_time.data)  # type: ignore
            record.end_at = datetime.combine(search_date, form.end_time.data)  # type: ignore
            record.description = form.description.data  # type: ignore
            record.is_archived = bool(form.is_archived.data)
            db.session.commit()
            return redirect(url_for("web_app.index", search_date=search_date))
        else:
            current_app.logger.error(f"Form validation failed: {form.errors}")
            abort(400)  # Bad Request

    return render_template("edit.html", form=form, record=record)


@web_app.route("/delete/<int:time_id>", methods=["GET", "POST"])
def delete(time_id):
    record = Timespan.query.get_or_404(time_id)
    form = TimespanDeleteForm(obj=record)

    if request.method == "POST":
        if form.validate_on_submit():
            search_date = record.search_date
            db.session.delete(record)
            db.session.commit()
            return redirect(url_for("web_app.index", search_date=search_date))
        else:
            current_app.logger.error(f"Form validation failed: {form.errors}")
            abort(400)  # Bad Request

    return render_template("delete.html", form=form, record=record)


@web_app.post("/toggle/<int:time_id>")
def toggle_checked(time_id):
    """Alternates `is_archived` status for selected record."""
    record = Timespan.query.get_or_404(time_id)
    record.is_archived = bool(not record.is_archived)
    db.session.commit()
    return ("", 204)


@web_app.get("/toggle/<int:time_id>")
@csrf.exempt
def toggle_checked_nojs(time_id):
    """Alternates `is_archived` status for selected record. For client without js."""
    toggle_checked(time_id)
    return redirect(request.referrer)


@web_app.get("/report")
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
