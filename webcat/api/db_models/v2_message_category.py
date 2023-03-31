from database import db

class MessageCategory_v2(db.Model):
    __tablename__ = 'message_categories_v2'
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages_v2.id', ondelete='CASCADE'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'))
    confidence = db.Column(db.Float, nullable=False)
    category = db.relationship('Category', backref=db.backref('message_categories_v2', lazy=True))
    # message = db.relationship('Message_v2', backref=db.backref('message_categories_v2', lazy=True))

    def __init__(self, message_id: int, category_id: int, confidence: float):
        self.message_id = message_id
        self.category_id = category_id
        self.confidence = confidence

    def __repr__(self):
        return f"MessageCategory_v2(id={self.id}, message_id={self.message_id}, category_id={self.category_id}, confidence={self.confidence})"
    
    def json_serialize(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'category_id': self.category_id,
            'confidence': self.confidence,
            'category': self.category.json_serialize()
        }