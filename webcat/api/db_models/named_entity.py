from database import db

class EntityType(db.Model):
    __tablename__ = 'entity_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    tag = db.Column(db.String(100))
    # entities = db.relationship('NamedEntity', backref='entity_types', lazy=True)

    def __init__(self, name: str, tag: str):
        self.name = name
        self.tag = tag

    def __repr__(self):
        return f"EntityType(id={self.id}, name={self.name}, tag={self.tag})"
    
    def json_serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'tag': self.tag
        }

class NamedEntity(db.Model):
    __tablename__ = 'named_entities'
    __mapper_args__ = {
        'confirm_deleted_rows': False
    }

    id = db.Column(db.Integer, primary_key=True)
    # when content is deleted, delete all named entities associated with it
    # content_id = db.Column(db.Integer, db.ForeignKey('contents.id', ondelete='CASCADE'))
    name = db.Column(db.String(100))
    type_id = db.Column(db.Integer, db.ForeignKey('entity_types.id'))
    type = db.relationship('EntityType', backref='named_entities', lazy=True)

    def __init__(self, name: str, type_id: int):
        self.name = name
        self.type_id = type_id

    def __repr__(self):
        return f"NamedEntity(id={self.id}, name={self.name}, type={self.type}, type_id={self.type_id})"

    def json_serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.json_serialize() # type must be fatched from db
        }