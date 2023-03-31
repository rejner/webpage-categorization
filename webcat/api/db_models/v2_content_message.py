from database import db

# binding table for one-to-many relationship between Content and Message
class ContentMessage_v2(db.Model):
    __tablename__ = 'content_messages_v2'
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('contents_v2.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('messages_v2.id'))
    # message = db.relationship('Message_v2', backref=db.backref('content_messages_v2', lazy=True))

    def __init__(self, content_id: int, message_id: int):
        self.content_id = content_id
        self.message_id = message_id

    def __repr__(self):
        return f"ContentMessage_v2(id={self.id}, content_id={self.content_id}, message_id={self.message_id})"

    def json_serialize(self):
        return {
            'id': self.id,
            'content_id': self.content_id,
            'message_id': self.message_id
        }
