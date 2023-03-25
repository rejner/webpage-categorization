import sys
from os import path
sys.path.append(path.dirname(__file__) + "/..")
sys.path.append(path.dirname(__file__) + "/../api")
import unittest
from flask_testing import TestCase
import api.api_v1 as api
import api.models_extension as models


class TestDatabases(TestCase):

    def create_app(self):
        self.app, self.db = api.create_app('config.py', bare=True)
        self.app.config['TESTING'] = True
        return self.app

    def setUp(self):
        self.db.create_all()
    
    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def add_category(self, name: str):
        category = models.Category(name)
        self.db.session.add(category)
        self.db.session.commit()
    
    def add_content(self, file_id: int, text: str):
        content = models.Content(file_id, text)
        self.db.session.add(content)
        self.db.session.commit()

    def add_file(self, name: str, path: str):
        file = models.File(name, path)
        self.db.session.add(file)
        self.db.session.commit()
    
    def add_entity(self, content_id: int, name: str, type_id: str):
        entity = models.NamedEntity(content_id, name, type_id)
        self.db.session.add(entity)
        self.db.session.commit()
    
    def add_entity_type(self, name: str, tag: str):
        entity_type = models.EntityType(name, tag)
        self.db.session.add(entity_type)
        self.db.session.commit()
    
    def add_content_category(self, content_id: int, category_id: int):
        content_category = models.ContentCategory(content_id, category_id)
        self.db.session.add(content_category)
        self.db.session.commit()
    
    def add_content_entity(self, content_id: int, entity_id: int):
        content_entity = models.ContentEntity(content_id, entity_id)
        self.db.session.add(content_entity)
        self.db.session.commit()

    def add_template(self, creation_date: str, origin_file: str):
        template = models.Template(creation_date, origin_file)
        self.db.session.add(template)
        self.db.session.commit()
    
    def add_element(self, tag: str, classes: list, id_attr: str, type: str):
        element = models.Element(tag, classes, id_attr, type)
        self.db.session.add(element)
        self.db.session.commit()
    
    def add_template_element(self, template_id: int, element_id: int):
        template_element = models.TemplateElement(template_id, element_id)
        self.db.session.add(template_element)
        self.db.session.commit()

    def test_create_category(self):
        self.add_category("test")
        categories = models.Category.query.all()
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].name, "test")

    
    def test_get_category(self):
        self.add_category("test")
        category = self.db.session.get(models.Category, 1)
        self.assertIsNotNone(category)
        self.assertEqual(category.name, "test")
    
    def test_get_all_categories(self):
        # add categories to db
        self.add_category("test")
        self.add_category("test")
        # retrieve data from db
        categories = models.Category.query.all()
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0].name, "test")
    
    def test_delete_category(self):
        # add category to db
        self.add_category("test")
        # delete category from db
        category = self.db.session.get(models.Category, 1)
        self.db.session.delete(category)
        self.db.session.commit()
        # retrieve data from db
        categories = models.Category.query.all()
        self.assertEqual(len(categories), 0)
    
    def test_create_content(self):
        # create file
        self.add_file("test", "test")
        # create a content
        self.add_content(1, "test text text text")
        # retrieve data from db
        contents = models.Content.query.all()
        self.assertEqual(len(contents), 1)
        self.assertEqual(contents[0].text, "test text text text")
    
    def test_content_with_category(self):
        self.add_file("test", "test")
        self.add_content(1, "test text text text")
        # create a category
        for cat_name in ["politics", "sport"]:
            self.add_category(cat_name)
        # add category to content
        self.add_content_category(1, 1)
        self.add_content_category(1, 2)
        # retrieve data from db
        content = self.db.session.get(models.Content, 1)
        self.assertEqual(len(content.categories), 2)
        self.assertEqual(content.categories[0].name, "politics")
        self.assertEqual(content.categories[1].name, "sport")     

    def test_content_with_entity(self):
        self.add_file("test", "test")
        self.add_content(1, "Petr Novak lives in New York.")
        for entity in [("person", "PER"), ("location", "LOC")]:
            self.add_entity_type(entity[0], entity[1])
        # create an entity
        for id, entity_name in enumerate(["Petr Novak", "New York"]):
            self.add_entity(1, entity_name, id+1)
        # add entity to content
        self.add_content_entity(1, 1)
        self.add_content_entity(1, 2)
        # retrieve data from db
        content = self.db.session.get(models.Content, 1)
        self.assertEqual(len(content.entities), 2)
        self.assertEqual(content.entities[0].name, "Petr Novak")
        self.assertEqual(content.entities[1].name, "New York")
        # get entity types and check them
        entity_type_1 = self.db.session.get(models.EntityType, 1)
        entity_type_2 = self.db.session.get(models.EntityType, 2)
        self.assertEqual(entity_type_1.name, "person")
        self.assertEqual(entity_type_2.name, "location")
        self.assertEqual(entity_type_1.tag, "PER")
        self.assertEqual(entity_type_2.tag, "LOC")

        # now delete content and check if entities are deleted
        self.db.session.delete(content)
        self.db.session.commit()
        entities = models.NamedEntity.query.all()
        self.assertEqual(len(entities), 0)

    def test_template(self):
        # create a template
        self.add_template("2020-01-01", "some_file.php")
        # retrieve data from db
        templates = models.Template.query.all()
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0].creation_date, "2020-01-01")
        self.assertEqual(templates[0].origin_file, "some_file.php")
    
    def test_template_element(self):
        # create a template
        self.add_template("2020-01-01", "some_file.php")
        elements = [
            ("div", ["class1", "class2"], "id1", "post-area"),
            ("div", ["class3", "class4"], "id2", "post-body"),
            ("div", ["class5", "class6"], "id3", "post-author"),
            ("div", ["class7", "class8"], "id4", "post-header")
        ]
        # create an element
        for element in elements:
            self.add_element(element[0], element[1], element[2], element[3])
        # create a template-element
        for id in range(1, 5):
            self.add_template_element(1, id)
        # retrieve data from db
        template = self.db.session.get(models.Template, 1)
        self.assertEqual(len(template.elements), 4)
        for id, element in enumerate(template.elements):
            self.assertEqual(element.tag, elements[id][0])
            self.assertEqual(element.classes, elements[id][1])
            self.assertEqual(element.id_attr, elements[id][2])
            self.assertEqual(element.type, elements[id][3])
        
    def test_template_cascade_delete(self):
        # create a template
        self.add_template("2020-01-01", "some_file.php")
        elements = [
            ("div", ["class1", "class2"], "id1", "post-area"),
            ("div", ["class3", "class4"], "id2", "post-body"),
        ]
        # create an element
        for element in elements:
            self.add_element(element[0], element[1], element[2], element[3])
        # delete template from db
        template = self.db.session.get(models.Template, 1)
        self.db.session.delete(template)
        self.db.session.commit()
        # retrieve data from db
        templates = models.Template.query.all()
        self.assertEqual(len(templates), 0)
        elements = models.TemplateElement.query.all()
        self.assertEqual(len(elements), 0)

    

if __name__ == "__main__":
    unittest.main()