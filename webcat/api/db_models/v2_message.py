from database import db

class Message_v2(db.Model):
    __tablename__ = 'messages_v2'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    categories = db.relationship('MessageCategory_v2', backref='messages_v2', lazy=True, cascade="all, delete-orphan", single_parent=True)
    entities = db.relationship('NamedEntity', backref='messages_v2', secondary='message_entities_v2', lazy=True, cascade="all, delete-orphan", single_parent=True)

    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        return f"Message_v2(id={self.id}, text={self.text}, categories={self.categories}, entities={self.entities})"
    
    def json_serialize(self):
        return {
            'id': self.id,
            'text': self.text,
            'categories': [c.json_serialize() for c in self.categories],
            'entities': [e.json_serialize() for e in self.entities]
        }
