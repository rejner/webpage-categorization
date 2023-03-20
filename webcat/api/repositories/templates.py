import json

class ElementType(enumerate):
    POST_AREA = 1
    POST_HEADER = 2
    POST_BODY = 3
    POST_AUTHOR = 4

ELEMENT_TYPE_MAP = {
    'post-area': ElementType.POST_AREA,
    'post-header': ElementType.POST_HEADER,
    'post-body': ElementType.POST_BODY,
    'post-author': ElementType.POST_AUTHOR
}

class Element:
    def __init__(self, id: int, tag: str, classes: list, id_attr: str, type: ElementType):
        self.id = id
        self.tag = tag
        self.classes = classes
        self.id_attr = id_attr
        self.type = type

    @staticmethod
    def from_json(json: dict):
        return Element(
            id=json['id'],
            tag=json['tag'],
            classes=json['classes'],
            id_attr=json['id_attr'],
            type=json['type']
        )

        
    
    def __repr__(self):
        return f"Element(id={self.id}, tag={self.tag}, classes={self.classes}, id_attr={self.id_attr}, type={self.type})"

class Template(object):
    def __init__(self, id: int, creation_date: str, origin_file: str, elements: list):
        self.id = id
        self.creation_date = creation_date
        self.origin_file = origin_file
        self.elements = elements
    
    @staticmethod
    def from_json(json: dict):
        return Template(
            id=json['id'],
            creation_date=json['creation_date'],
            origin_file=json['origin_file'],
            elements=[Element.from_json(e) for e in json['elements']]
        )
    
    def __repr__(self):
        return f"Template(id={self.id}, creation_date={self.creation_date}, origin_file={self.origin_file}, elements={self.elements})"
    

class TemplateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Template):
            return {
                'id': o.id,
                'creation_date': o.creation_date,
                'origin_file': o.origin_file,
                'elements': [self.default(e) for e in o.elements]
            }
        elif isinstance(o, Element):
            return {
                'id': o.id,
                'tag': o.tag,
                'classes': o.classes,
                'id_attr': o.id_attr,
                'type': o.type
            }
        else:
            return super().default(o)


class TemplatesRepository():
    def __init__(self, conn):
        self.conn = conn

    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS elements (id serial PRIMARY KEY,'
                                            'tag varchar (150) NOT NULL,'
                                            'classes varchar (150) [],'
                                            'id_attr varchar (150) NOT NULL,'
                                            'type text NOT NULL);'
                                            )

        cur.execute('CREATE TABLE IF NOT EXISTS templates (id serial PRIMARY KEY,'
                                            'creation_date timestamp DEFAULT CURRENT_TIMESTAMP,'
                                            'origin_file varchar (150) NOT NULL);'
                                            )

        cur.execute('CREATE TABLE IF NOT EXISTS element_template (id serial PRIMARY KEY,'
                                            'element_id integer NOT NULL,'
                                            'template_id integer NOT NULL,'
                                            'FOREIGN KEY (element_id) REFERENCES elements(id) ON DELETE CASCADE,'
                                            'FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE);')
        cur.close()
        self.conn.commit()
    
    def drop_tables(self):
        cur = self.conn.cursor()
        cur.execute('DROP TABLE IF EXISTS element_template;')
        cur.execute('DROP TABLE IF EXISTS templates;')
        cur.execute('DROP TABLE IF EXISTS elements;')
        cur.close()
        self.conn.commit()

    def init_repository(self):
        self.drop_tables()
        self.create_tables()

    def get_all(self):
        # get templates and all their elements from db
        # element ids are stored in element_template table
        # elements are stored in elements table
        # templates are stored in templates table
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM templates;')
        templates = cur.fetchall()
        templates = [self._get_template(template) for template in templates]
        cur.close()
        return templates
    
    def _get_template(self, template):
        # get id of template
        template_id = template[0]
        # get all element ids from element_template table where template_id = template_id
        cur = self.conn.cursor()
        cur.execute('SELECT element_id FROM element_template WHERE template_id = %s;', (template_id,))
        element_ids = cur.fetchall()
        elements_ids = tuple([el[0] for el in element_ids])
        # now get all records from elements with returned ids
        cur.execute('SELECT * FROM elements WHERE id IN %s;', (elements_ids,))
        elements = cur.fetchall()
        cur.close()
        template_object = Template(*template, [Element(*el) for el in elements])
        template_object.creation_date = template_object.creation_date.strftime('%Y-%m-%d %H:%M:%S')
        return template_object
    
    def get_by_id(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM templates WHERE id = %s;', (id,))
        template = cur.fetchone()
        cur.close()
        template = self._get_template(template)
        return template

    def delete(self, id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM templates WHERE id = %s;', (id,))
        self.conn.commit()
        cur.close()

    def create(self, template: Template) -> Template:
        cur = self.conn.cursor()
        cur.execute('INSERT INTO templates (origin_file) VALUES (%s) RETURNING id;', (template.origin_file,))
        template_id = cur.fetchone()[0]
        for element in template.elements:
            self._create_element(element, template_id, cur)
        self.conn.commit()
        cur.close()
        # fetch template from db and return it
        template = self.get_by_id(template_id)
        return template

        
    def _create_element(self, element: Element, template_id: int, cur):
        cur.execute('INSERT INTO elements (tag, classes, id_attr, type) VALUES (%s, %s, %s, %s) RETURNING id;', (element.tag, element.classes, element.id_attr, element.type))
        element_id = cur.fetchone()[0]
        cur.execute('INSERT INTO element_template (element_id, template_id) VALUES (%s, %s);', (element_id, template_id))





    