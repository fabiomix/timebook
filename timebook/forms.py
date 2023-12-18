from datetime import date

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, StringField, SubmitField, TimeField
from wtforms.validators import DataRequired


class TimespanCreateForm(FlaskForm):
    description = StringField("Description", validators=[DataRequired()])
    start_time = TimeField("Start time", validators=[DataRequired()])
    end_time = TimeField("End time", validators=[DataRequired()])
    search_date = DateField("Date", validators=[DataRequired()], default=date.today)
    submit = SubmitField("Save")


class TimespanEditForm(TimespanCreateForm):
    is_archived = BooleanField("Archived")


class TimespanDeleteForm(FlaskForm):
    submit = SubmitField("Yes, delete this record")
