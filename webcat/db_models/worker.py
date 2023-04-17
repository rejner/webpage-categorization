from webcat.database import db

class Worker(db.Model):
    __tablename__ = 'workers'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256))
    status = db.Column(db.String(32))
    type = db.Column(db.String(32))

    def __init__(self, url: str, status: str, type: str):
        self.url = url
        self.status = status
        self.type = type
    
    def __repr__(self):
        return f"Worker(id={self.id}, url={self.url}, status={self.status}, type={self.type})"
    
    def json_serialize(self):
        return {
            'id': self.id,
            'url': self.url,
            'status': self.status,
            'type': self.type
        }
