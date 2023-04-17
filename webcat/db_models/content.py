from webcat.database import db

class Content(db.Model):
    __tablename__ = 'contents'
    id = db.Column(db.Integer, primary_key=True)
    attributes = db.relationship('Attribute', secondary='content_attributes', backref=db.backref('contents', lazy=True, cascade="all")) 
    hash = db.Column(db.String(32), unique=True)
    foreign_identity = db.Column(db.String(255), nullable=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    file = db.relationship('File', backref=db.backref('contents', lazy=True))
    
    def __init__(self, hash: str, foreign_identity: str = None):
        self.hash = hash
        self.foreign_identity = foreign_identity

    def __repr__(self):
        return f"Content(id={self.id}, file={self.file}, hash={self.hash} foreign_identity={self.foreign_identity})"

    def json_serialize(self):
        return {
            'id': self.id,
            'file': self.file.json_serialize(),
            'attributes': [attribute.json_serialize() for attribute in self.attributes],
            'hash': self.hash,
            'foreign_identity': self.foreign_identity
        }



    

    


    


