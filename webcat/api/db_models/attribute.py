from database import db

class Attribute(db.Model):
    __tablename__ = 'attributes'
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('attribute_types.id'), nullable=False)
    content = db.Column(db.Text)
    type = db.relationship('AttributeType', backref='attributes', lazy=True, cascade="all, delete-orphan", single_parent=True)
    tag = db.Column(db.String(100), nullable=True) # can contain additional information about the attribute, e.g. counter, etc.
    categories = db.relationship('AttributeCategory', backref='attributes', lazy=True, cascade="all, delete-orphan", single_parent=True)
    entities = db.relationship('NamedEntity', backref='attributes', secondary='attribute_entities', lazy=True, cascade="all, delete-orphan", single_parent=True)

    def __init__(self, type_id: int, content: str, tag: str = None):
        self.type_id = type_id
        self.content = content
        self.tag = tag

    def __repr__(self):
        return f"Attribute(id={self.id}, type_id={self.type_id}, content={self.content}, categories={self.categories}, entities={self.entities} tag={self.tag})"
    
    def json_serialize(self):
        return {
            'id': self.id,
            'type_id': self.type_id,
            'content': self.content,
            'tag': self.tag,
            'categories': [c.json_serialize() for c in self.categories],
            'entities': [e.json_serialize() for e in self.entities],
            'type': self.type.json_serialize()
        }