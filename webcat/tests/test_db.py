

import sys
from os import path
sys.path.append(path.dirname(__file__) + "/..")
sys.path.append(path.dirname(__file__) + "/../api")
import unittest
from flask_testing import TestCase
import api.api_v1 as v1


class TestDatabases(TestCase):

    def create_app(self):
        self.app, self.db = v1.create_app('config.py')
        self.app.config['TESTING'] = True
        return self.app

    def setUp(self):
        self.db.create_all()
    
    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def add_category(self, name: str):
        category = v1.Category(name)
        self.db.session.add(category)
        self.db.session.commit()
    
    def add_content(self, file_id: int, text: str):
        content = v1.Content(file_id, text)
        self.db.session.add(content)
        self.db.session.commit()

    def add_file(self, name: str, path: str):
        file = v1.File(name, path)
        self.db.session.add(file)
        self.db.session.commit()
    
    def add_entity(self, content_id: int, name: str, type_id: str):
        entity = v1.NamedEntity(content_id, name, type_id)
        self.db.session.add(entity)
        self.db.session.commit()
    
    def add_entity_type(self, name: str, tag: str):
        entity_type = v1.EntityType(name, tag)
        self.db.session.add(entity_type)
        self.db.session.commit()
    
    def add_content_category(self, content_id: int, category_id: int):
        content_category = v1.ContentCategory(content_id, category_id)
        self.db.session.add(content_category)
        self.db.session.commit()
    
    def add_content_entity(self, content_id: int, entity_id: int):
        content_entity = v1.ContentEntity(content_id, entity_id)
        self.db.session.add(content_entity)
        self.db.session.commit()

    def test_create_category(self):
        self.add_category("test")
        categories = v1.Category.query.all()
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].name, "test")

    
    def test_get_category(self):
        self.add_category("test")
        category = self.db.session.get(v1.Category, 1)
        self.assertIsNotNone(category)
        self.assertEqual(category.name, "test")
    
    def test_get_all_categories(self):
        # add categories to db
        self.add_category("test")
        self.add_category("test")
        # retrieve data from db
        categories = v1.Category.query.all()
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0].name, "test")
    
    def test_delete_category(self):
        # add category to db
        self.add_category("test")
        # delete category from db
        category = self.db.session.get(v1.Category, 1)
        self.db.session.delete(category)
        self.db.session.commit()
        # retrieve data from db
        categories = v1.Category.query.all()
        self.assertEqual(len(categories), 0)
    
    def test_create_content(self):
        # create file
        self.add_file("test", "test")
        # create a content
        self.add_content(1, "test text text text")
        # retrieve data from db
        contents = v1.Content.query.all()
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
        content = self.db.session.get(v1.Content, 1)
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
        content = self.db.session.get(v1.Content, 1)
        self.assertEqual(len(content.entities), 2)
        self.assertEqual(content.entities[0].name, "Petr Novak")
        self.assertEqual(content.entities[1].name, "New York")
        # get entity types and check them
        entity_type_1 = self.db.session.get(v1.EntityType, 1)
        entity_type_2 = self.db.session.get(v1.EntityType, 2)
        self.assertEqual(entity_type_1.name, "person")
        self.assertEqual(entity_type_2.name, "location")
        self.assertEqual(entity_type_1.tag, "PER")
        self.assertEqual(entity_type_2.tag, "LOC")

        # now delete content and check if entities are deleted
        self.db.session.delete(content)
        self.db.session.commit()
        entities = v1.NamedEntity.query.all()
        self.assertEqual(len(entities), 0)

    

if __name__ == "__main__":
    unittest.main()