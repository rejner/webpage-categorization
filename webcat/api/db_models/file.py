from database import db

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    path = db.Column(db.Text)
    contents = db.relationship('Content', backref='files', lazy=True, cascade="all")

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path

    def __repr__(self):
        return f"File(id={self.id}, name={self.name}, path={self.path})"

    def json_serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path
        }