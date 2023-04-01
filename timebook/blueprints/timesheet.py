from datetime import date, datetime

from flask import request, render_template, redirect, url_for
from flask import current_app, Blueprint
from flask_babel import format_date

from timebook.models import Timesheet
from timebook import db

BABEL_DEFAULT_DATE_FORMAT = "EEEE d MMMM yyyy"

timesheet_app = Blueprint('timesheet_app', __name__)


@timesheet_app.get('/')
def index():
    """The main page, shows timespan from selected date (or today)."""
    try:
        today_isoformat = date.today().isoformat()
        from_date = request.args.get('from_date', today_isoformat)
        from_date = date.fromisoformat(from_date)
    except ValueError:
        from_date = today_isoformat
    # get daily lines
    lines = Timesheet.query.filter_by(day=from_date).order_by(Timesheet.end_time).all()
    # do the math here
    total_time = sum([t.duration for t in lines])
    total_time = Timesheet.float_time_to_time(total_time)
    # prettify selected date
    from_date = format_date(from_date, BABEL_DEFAULT_DATE_FORMAT)
    # finally render page
    return render_template('index.html', from_date=from_date, lines=lines, total_time=total_time)

@timesheet_app.post('/')
def create_timesheet():
    """Submit a new timesheet record for creation."""
    form_data = request.form.to_dict(flat=True)
    today_isoformat = date.today().isoformat()
    # defaults and parsing
    day = form_data.get('day', today_isoformat)
    description = form_data.get('description', '/')
    end_time = form_data.get('end_time', '11:00')
    duration = form_data.get('duration', '00:15')
    # creating timesheet object
    new_timesheet = Timesheet(description, day, end_time, duration)
    # store in database and go back to home
    db.session.add(new_timesheet)
    db.session.commit()
    return redirect(request.referrer)

@timesheet_app.get('/edit/<int:time_id>')
def read_timesheet(time_id):
    """Edit page for updating an existing record."""
    record = Timesheet.query.get_or_404(time_id)
    return render_template('edit.html', record=record)

@timesheet_app.post('/edit/<int:time_id>')
def update_timesheet(time_id):
    """Submit an update for an existing record."""
    record = Timesheet.query.get_or_404(time_id)
    form_data = request.form.to_dict(flat=True)
    if form_data.get('description', False):
        record.description = form_data['description']
    if form_data.get('day', False):
        record.day = Timesheet.convert_day(form_data['day'])
    if form_data.get('end_time', False):
        record.end_time = Timesheet.time_to_float_time(form_data['end_time'])
    if form_data.get('duration', False):
        record.duration = Timesheet.time_to_float_time(form_data['duration'])
    db.session.commit()
    return redirect(url_for('timesheet_app.index'))
