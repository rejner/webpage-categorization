from database import db

# create SQLAlchemy models
class Content_v2(db.Model):
    __tablename__ = 'contents_v2'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Text)
    header = db.Column(db.Text)
    messages = db.relationship('Message_v2', secondary='content_messages_v2', backref=db.backref('contents_v2', lazy=True))
    hash = db.Column(db.String(32), unique=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    file = db.relationship('File', backref=db.backref('contents_v2', lazy=True))
    
    def __init__(self, hash: str, author: str, header: str):
        self.hash = hash
        self.author = author
        self.header = header

    def __repr__(self):
        return f"Content(id={self.id}, file={self.file}, author={self.author}, header={self.header}, messages={self.messages}, hash={self.hash})"

    def json_serialize(self):
        return {
            'id': self.id,
            'file': self.file.json_serialize(),
            'author': self.author,
            'header': self.header,
            'messages': [m.json_serialize() for m in self.messages],
            'hash': self.hash,
        }



    

    


    


