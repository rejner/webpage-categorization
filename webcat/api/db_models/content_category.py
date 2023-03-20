from database import db

class ContentCategory(db.Model):
    __tablename__ = 'content_categories'
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('contents.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    def __init__(self, content_id: int, category_id: int):
        self.content_id = content_id
        self.category_id = category_id

