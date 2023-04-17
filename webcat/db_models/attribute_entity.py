from webcat.database import db

class AttributeEntity(db.Model):
    __tablename__ = 'attribute_entities'
    id = db.Column(db.Integer, primary_key=True)
    attribute_id = db.Column(db.Integer, db.ForeignKey('attributes.id', ondelete='CASCADE'))
    entity_id = db.Column(db.Integer, db.ForeignKey('named_entities.id', ondelete='CASCADE'))

    def __init__(self, attribute_id: int, entity_id: int):
        self.attribute_id = attribute_id
        self.entity_id = entity_id

    def __repr__(self):
        return f"AttributeEntity(id={self.id}, attribute_id={self.attribute_id}, entity_id={self.entity_id})"

    def json_serialize(self):
        return {
            'id': self.id,
            'attribute_id': self.attribute_id,
            'entity_id': self.entity_id
        }