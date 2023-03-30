from database import db

# binding table of templates and elements
class TemplateElement_v2(db.Model):
    __tablename__ = 'template_elements_v2'
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('templates_v2.id'))
    element_id = db.Column(db.Integer, db.ForeignKey('elements_v2.id'))

    def __init__(self, template_id: int, element_id: int):
        self.template_id = template_id
        self.element_id = element_id

    def __repr__(self):
        return f"TemplateElement_v2(id={self.id}, template_id={self.template_id}, element_id={self.element_id})"
