from datetime import datetime, time, timedelta

from sqlalchemy.ext.hybrid import hybrid_property

from timebook import db


class Timespan(db.Model):
    __tablename__ = "timespan"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)  # primary keys are required by SQLAlchemy
    description: str = db.Column(db.String(500), nullable=False)
    start_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_at: datetime = db.Column(db.DateTime, nullable=True)
    is_archived: bool = db.Column(db.Boolean, nullable=False, default=False)
    created_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Timespan id={self.id}>"

    def __init__(self, description: str, start_at: datetime, end_at: datetime):
        self.description = description
        self.start_at = start_at
        self.end_at = end_at
        self.is_archived = False

    @hybrid_property
    def start_time(self) -> time:
        return self.start_at.time()

    @hybrid_property
    def end_time(self) -> time:
        return self.end_at.time()

    @hybrid_property
    def duration(self) -> timedelta:
        return self.end_at - self.start_at

    def to_string(self) -> str:
        start_date = self.start_at.date().isoformat()
        start_time = self.start_at.time().isoformat(timespec="minutes")
        end_time = self.end_at.time().isoformat(timespec="minutes")
        return f"{start_date} from {start_time} to {end_time} for {self.duration}: {self.description} [id={self.id}]"
