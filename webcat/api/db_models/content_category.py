from database import db

class ContentCategory(db.Model):
    __tablename__ = 'content_categories'
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('contents.id', ondelete='CASCADE'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'))
    category = db.relationship('Category', backref=db.backref('content_categories', lazy=True))
    confidence = db.Column(db.Float, nullable=False)

    def __init__(self, content_id: int, category_id: int, confidence: float):
        self.content_id = content_id
        self.category_id = category_id
        self.confidence = confidence
    
    def __repr__(self):
        return f"ContentCategory(id={self.id}, content_id={self.content_id}, category_id={self.category_id}, confidence={self.confidence}, category={self.category})"

