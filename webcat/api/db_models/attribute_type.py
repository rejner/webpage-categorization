from database import db

class AttributeType(db.Model):
    __tablename__ = 'attribute_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    tag = db.Column(db.String(100))
    analyzed = db.Column(db.Boolean)

    def __init__(self, name: str, tag: str, analyzed: bool = False):
        self.name = name
        self.tag = tag
        self.analyzed = analyzed

    def __repr__(self):
        return f"AttributeType(id={self.id}, name={self.name}, tag={self.tag} analyzed={self.analyzed})"
    
    def json_serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'tag': self.tag,
            'analyzed': self.analyzed
        }