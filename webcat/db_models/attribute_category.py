from webcat.database import db

class AttributeCategory(db.Model):
    __tablename__ = 'attribute_categories'
    id = db.Column(db.Integer, primary_key=True)
    attribute_id = db.Column(db.Integer, db.ForeignKey('attributes.id', ondelete='CASCADE'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'))
    score = db.Column(db.Float, nullable=False)
    category = db.relationship('Category', backref=db.backref('attribute_categories', lazy=True))

    def __init__(self, attribute_id: int, category_id: int, score: float):
        self.attribute_id = attribute_id
        self.category_id = category_id
        self.score = score

    def __repr__(self):
        return f"AttributeCategory(id={self.id}, attribute_id={self.attribute_id}, category_id={self.category_id}, score={self.score})"
    
    def json_serialize(self):
        return {
            'id': self.id,
            'attribute_id': self.attribute_id,
            'category_id': self.category_id,
            'score': self.score,
            'category': self.category.json_serialize()
        }