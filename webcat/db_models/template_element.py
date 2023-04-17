from webcat.database import db

# binding table of templates and elements
class TemplateElement(db.Model):
    __tablename__ = 'template_elements'
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'))
    element_id = db.Column(db.Integer, db.ForeignKey('elements.id'))

    def __init__(self, template_id: int, element_id: int):
        self.template_id = template_id
        self.element_id = element_id

    def __repr__(self):
        return f"TemplateElement(id={self.id}, template_id={self.template_id}, element_id={self.element_id})"
