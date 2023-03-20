from database import db

class EntityType(db.Model):
    __tablename__ = 'entity_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    tag = db.Column(db.String(100))
    entities = db.relationship('NamedEntity', backref='entity_types', lazy=True)

    def __init__(self, name: str, tag: str):
        self.name = name
        self.tag = tag

    def __repr__(self):
        return f"EntityType(id={self.id}, name={self.name}, tag={self.tag})"

class NamedEntity(db.Model):
    __tablename__ = 'named_entities'
    id = db.Column(db.Integer, primary_key=True)
    # when content is deleted, delete all named entities associated with it
    content_id = db.Column(db.Integer, db.ForeignKey('contents.id', ondelete='CASCADE'))
    name = db.Column(db.String(100))
    type_id = db.Column(db.Integer, db.ForeignKey('entity_types.id'))

    def __init__(self, content_id: int, name: str, type_id: int):
        self.content_id = content_id
        self.name = name
        self.type_id = type_id

    def __repr__(self):
        return f"NamedEntity(id={self.id}, name={self.name}, type={self.type})"