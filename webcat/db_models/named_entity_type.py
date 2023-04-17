from webcat.database import db

class NamedEntityType(db.Model):
    __tablename__ = 'named_entity_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    tag = db.Column(db.String(100))

    def __init__(self, name: str, tag: str):
        self.name = name
        self.tag = tag

    def __repr__(self):
        return f"NamedEntityType(id={self.id}, name={self.name}, tag={self.tag})"
    
    def json_serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'tag': self.tag
        }