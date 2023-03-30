from database import db

class Template_v2(db.Model):
    __tablename__ = 'templates_v2'
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.String(100))
    origin_file = db.Column(db.Text)
    elements = db.relationship('Element_v2', backref='templates_v2', secondary='template_elements_v2', lazy=True, cascade="all, delete-orphan", single_parent=True)

    def __init__(self, creation_date: str, origin_file: str):
        self.creation_date = creation_date
        self.origin_file = origin_file
    
    def json_serialize(self):
        return {
            'id': self.id,
            'creation_date': self.creation_date,
            'origin_file': self.origin_file,
            'elements': [e.json_serialize() for e in self.elements]
        }
