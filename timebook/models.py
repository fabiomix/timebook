from datetime import date, datetime

from flask import abort

from timebook import db


class Timesheet(db.Model):
    __tablename__ = "timesheet"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # primary keys are required by SQLAlchemy
    description = db.Column(db.String(1000), nullable=False)
    day = db.Column(db.Date, nullable=False)
    end_time = db.Column(db.Numeric(precision=4, scale=2), nullable=False)
    duration = db.Column(db.Numeric(precision=4, scale=2), nullable=False)
    is_checked = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, description, day, end_time, duration):
        self.description = description
        self.day = Timesheet.convert_day(day)
        self.end_time = Timesheet.time_to_float_time(end_time)
        self.duration = Timesheet.time_to_float_time(duration)
        self.is_checked = False

    def __repr__(self):
        return "<timesheet {}>".format(self.id)

    def get_start_time(self) -> float:
        """Compute the start time of this timespan."""
        return self.end_time - self.duration

    # the following methods are staticmethod so they are easily callable
    # from jinja templates.

    @staticmethod
    def convert_day(value: str) -> date:
        """Shortcut to convert YYYY-MM-DD to date object."""
        day = date.fromisoformat(value)
        return day

    @staticmethod
    def time_to_float_time(value: str) -> float:
        """Convert string time (ex. '01:30') into float_time (ex. 1.50)."""
        hour, minute = value.split(":")
        return int(hour) + int(minute) / 60.0

    @staticmethod
    def float_time_to_time(value: float) -> str:
        """Convert float_time (ex. 2.75) into time string (ex. '02:45')."""
        return "{0:02.0f}:{1:02.0f}".format(*divmod(float(value) * 60, 60))
