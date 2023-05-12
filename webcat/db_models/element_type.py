from webcat.database import db

class ElementType(db.Model):
    __tablename__ = 'element_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    tag = db.Column(db.String(100))
    analysis_flag = db.Column(db.Boolean)

    def __init__(self, name: str, tag: str = None, analysis_flag: bool = False):
        self.name = name
        self.tag = tag if tag else name
        self.analysis_flag = analysis_flag

    def __repr__(self):
        return f"ElementType(id={self.id}, name={self.name}, tag={self.tag}, analysis_flag={self.analysis_flag})"

    def json_serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'tag': self.tag,
            'analysis_flag': self.analysis_flag
        }