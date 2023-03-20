from database import db

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Category(id={self.id}, name={self.name})"
    