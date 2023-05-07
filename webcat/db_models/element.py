from webcat.database import db

class Element(db.Model):
    __tablename__ = 'elements'

    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('element_types.id'))
    type = db.relationship('ElementType', backref=db.backref('elements', lazy=True, cascade="all, delete-orphan", single_parent=True))
    tag = db.Column(db.String(100))
    parent_tag = db.Column(db.String(100))
    grandparent_tag = db.Column(db.String(100))
    depth = db.Column(db.Integer)
    xPath = db.Column(db.Text)
    classes = db.Column(db.Text)

    def __init__(self, tag: str, type_id: int, parent_tag: str, grandparent_tag: str, depth: int, xPath: str, classes: str):
        self.tag = tag
        self.type_id = type_id
        self.parent_tag = parent_tag
        self.grandparent_tag = grandparent_tag
        self.depth = depth
        self.xPath = xPath
        self.classes = classes
        

    def __repr__(self):
        return f"Element(id={self.id}, tag={self.tag}, parent_tag={self.parent_tag}, grandparent_tag={self.grandparent_tag}, depth={self.depth} type_id={self.type_id}, xPath={self.xPath}, classes={self.classes})"

    def json_serialize(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'type_id': self.type_id,
            'parent_tag': self.parent_tag,
            'grandparent_tag': self.grandparent_tag,
            'depth': self.depth,
            'type': self.type.json_serialize(),
            'xPath': self.xPath,
            'classes': self.classes
        }