from database import db

class ContentEntity(db.Model):
    __tablename__ = 'content_entities'
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('contents.id'))
    entity_id = db.Column(db.Integer, db.ForeignKey('named_entities.id'))

    def __init__(self, content_id: int, entity_id: int):
        self.content_id = content_id
        self.entity_id = entity_id

    def __repr__(self):
        return f"ContentEntity(id={self.id}, content_id={self.content_id}, entity_id={self.entity_id}, entity_type_id={self.entity_type_id})"
