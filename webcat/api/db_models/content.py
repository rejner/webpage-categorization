from database import db

# create SQLAlchemy models
class Content(db.Model):
    __tablename__ = 'contents'
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    # file is stored in the database in 'files' table
    
    text = db.Column(db.String(10000))
    # categories = db.relationship('Category', lazy=True, secondary='content_categories', cascade="all, delete-orphan", single_parent=True)
    entities = db.relationship('NamedEntity', lazy=True, secondary='content_entities', cascade="all, delete-orphan", single_parent=True)
    # confirences are stored in a column together with contet_categories table as a float
    # create relationship to 'content_categories' table, column 'confidence'
    categories = db.relationship('ContentCategory', lazy=True, cascade="all, delete-orphan", single_parent=True)
    
    def __init__(self, file_id: int, text: str):
        self.file_id = file_id
        self.text = text

    def __repr__(self):
        return f"Content(id={self.id}, file_id={self.file_id}, text={self.text}, categories={self.categories}, entities={self.entities})"

    def json_serialize(self):
        return {
            'id': self.id,
            'file_id': self.file_id,
            'text': self.text,
            'categories': [c.json_serialize() for c in self.categories],
            'entities': [e.json_serialize() for e in self.entities]
        }



    

    


    


