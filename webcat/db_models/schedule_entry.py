from webcat.database import db

class ScheduleEntry(db.Model):
    __tablename__ = 'schedule_entries'
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'))
    worker = db.relationship('Worker', backref=db.backref('schedule_entries', lazy=True))
    file_path = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, worker_id: int, file_path: str):
        self.worker_id = worker_id
        self.file_path = file_path

    def __repr__(self):
        return f"ScheduleEntry(id={self.id}, worker_id={self.worker_id}, file_path={self.file_path}, created_at={self.created_at})"
    
    def json_serialize(self):
        return {
            'id': self.id,
            'worker': self.worker.json_serialize(),
            'file_path': self.file_path,
            'created_at': self.created_at
        }
