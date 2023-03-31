from database import db

class MessageEntity_v2(db.Model):
    __tablename__ = 'message_entities_v2'
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages_v2.id', ondelete='CASCADE'))
    entity_id = db.Column(db.Integer, db.ForeignKey('named_entities.id', ondelete='CASCADE'))
    # entity = db.relationship('NamedEntity', backref=db.backref('message_entities_v2', lazy=True))
    # message = db.relationship('Message_v2', backref=db.backref('message_entities_v2', lazy=True))

    def __init__(self, message_id: int, entity_id: int):
        self.message_id = message_id
        self.entity_id = entity_id

    def __repr__(self):
        return f"MessageEntity_v2(id={self.id}, message_id={self.message_id}, entity_id={self.entity_id}, entity={self.entity})"

    def json_serialize(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'entity_id': self.entity_id,
            'entity': self.entity.json_serialize()
        }