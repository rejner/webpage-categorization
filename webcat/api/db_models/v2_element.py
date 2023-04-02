from database import db

class Element_v2(db.Model):
    __tablename__ = 'elements_v2'

    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('element_types_v2.id'))
    tag = db.Column(db.String(100))
    parent_tag = db.Column(db.String(100))
    grandparent_tag = db.Column(db.String(100))
    depth = db.Column(db.Integer)

    def __init__(self, tag: str, type_id: int, parent_tag: str, grandparent_tag: str, depth: int):
        self.tag = tag
        self.type_id = type_id
        self.parent_tag = parent_tag
        self.grandparent_tag = grandparent_tag
        self.depth = depth
        

    def __repr__(self):
        return f"Element_v2(id={self.id}, tag={self.tag}, parent_tag={self.parent_tag}, grandparent_tag={self.grandparent_tag}, depth={self.depth} type_id={self.type_id})"

    def json_serialize(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'type_id': self.type_id,
            'parent_tag': self.parent_tag,
            'grandparent_tag': self.grandparent_tag,
            'depth': self.depth
        }