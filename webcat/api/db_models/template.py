from database import db

class Template(db.Model):
    __tablename__ = 'templates'
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.String(100))
    origin_file = db.Column(db.String(100))
    elements = db.relationship('Element', backref='templates', lazy=True)

    def __init__(self, creation_date: str, origin_file: str):
        self.creation_date = creation_date
        self.origin_file = origin_file
