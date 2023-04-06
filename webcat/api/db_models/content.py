from database import db

class Content(db.Model):
    __tablename__ = 'contents'
    id = db.Column(db.Integer, primary_key=True)
    attributes = db.relationship('Attribute', secondary='content_attributes', backref=db.backref('contents', lazy=True))
    hash = db.Column(db.String(32), unique=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    file = db.relationship('File', backref=db.backref('contents', lazy=True))
    
    def __init__(self, hash: str):
        self.hash = hash

    def __repr__(self):
        return f"Content(id={self.id}, file={self.file}, hash={self.hash})"

    def json_serialize(self):
        return {
            'id': self.id,
            'file': self.file.json_serialize(),
            'attributes': [attribute.json_serialize() for attribute in self.attributes],
            'hash': self.hash,
        }



    

    


    


