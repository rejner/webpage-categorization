from database import db

# create SQLAlchemy models
class Content(db.Model):
    __tablename__ = 'contents'
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    text = db.Column(db.String(10000))
    categories = db.relationship('Category', backref='contents', lazy=True, secondary='content_categories', cascade="all, delete-orphan", single_parent=True)
    entities = db.relationship('NamedEntity', backref='contents', lazy=True, secondary='content_entities', cascade="all, delete-orphan", single_parent=True)

    def __init__(self, file_id: int, text: str):
        self.file_id = file_id
        self.text = text

    def __repr__(self):
        return f"Content(id={self.id}, file_id={self.file_id}, text={self.text}, categories={self.categories}, entities={self.entities})"




    

    


    


