from database import db

class ElementType_v2(db.Model):
    __tablename__ = 'element_types_v2'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    elements = db.relationship('Element_v2', backref='element_types_v2', lazy=True, cascade="all, delete-orphan", single_parent=True)

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"ElementType_v2(id={self.id}, name={self.name})"

    def json_serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }