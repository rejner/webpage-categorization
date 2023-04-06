from database import db

# binding table for one-to-many relationship between Content and Message
class ContentAttribute(db.Model):
    __tablename__ = 'content_attributes'
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('contents.id'))
    attribute_id = db.Column(db.Integer, db.ForeignKey('attributes.id'))


    def __init__(self, content_id: int, attribute_id: int):
        self.content_id = content_id
        self.attribute_id = attribute_id

    def __repr__(self):
        return f"ContentAttribute(id={self.id}, content_id={self.content_id}, attribute_id={self.attribute_id})"

    def json_serialize(self):
        return {
            'id': self.id,
            'content_id': self.content_id,
            'attribute_id': self.attribute_id
        }
