from database import db

class Element(db.Model):
    __tablename__ = 'elements'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(100))
    classes = db.Column(db.ARRAY(db.String))
    id_attr = db.Column(db.String(100))
    type = db.Column(db.String(100))
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'))

    def __init__(self, tag: str, classes: list, id_attr: str, type: str):
        self.tag = tag
        self.classes = classes
        self.id_attr = id_attr
        self.type = type

    def __repr__(self):
        return f"Element(id={self.id}, tag={self.tag}, classes={self.classes}, id_attr={self.id_attr}, type={self.type})"
