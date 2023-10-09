from datetime import date, timedelta

from flask import abort, current_app, request


def ensure_valid_date(input_date: str) -> date:
    """Parse input date, set default if missing, error if invalid."""
    try:
        today_isoformat = date.today().isoformat()
        search_date = date.fromisoformat(input_date or today_isoformat)
    except (ValueError, TypeError) as e:
        current_app.logger.info(e)
        abort(400)  # Bad Request
    return search_date


def ensure_required_fields() -> dict:
    """Ensure required fields are present in form data."""
    form_data = request.form.to_dict()
    if not form_data.get("description", False):
        abort(400)  # Bad Request
    if not form_data.get("start_time", False):
        abort(400)  # Bad Request
    if not form_data.get("end_time", False):
        abort(400)  # Bad Request
    return form_data


def format_timedelta(td: timedelta, force_full=False) -> str:
    """Format a timedelta object into a human-readable string."""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if force_full:
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
    elif hours == 0 and minutes:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif hours and minutes == 0:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        return f"{hours}h {minutes}m"
