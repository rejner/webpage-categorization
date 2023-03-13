

import sys
from os import path
sys.path.append(path.dirname(__file__) + "/..")
import unittest
import psycopg2
import api.repository.templates as t

class TestDatabases(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.conn = psycopg2.connect(
            host="host.docker.internal",
            database="webcat_db",
            user='postgres',
            password='postgres',
            port=5432)
        self.template_repository = t.TemplatesRepository(self.conn)
    
    def _fill_db(self):
        self.template_repository.create(
            t.Template(
                id=0,
                origin_file="test.html",
                creation_date=None,
                elements=[
                    t.Element(
                        id=0,
                        tag="div",
                        classes=["post", "post-wrapper"],
                        id_attr="post-1",
                        type="post-area"
                    ),
                    t.Element(
                        id=0,
                        tag="div",
                        classes=["post-header"],
                        id_attr="post-header-1",
                        type="post-header"
                    )
                ]
            )
        )

    def test_get_all_templates(self):
        self.template_repository.init_repository()
        self._fill_db()
        templates = self.template_repository.get_all()
        self.assertIsNotNone(templates)
        self.assertEqual(len(templates), 1)

    def test_create_template(self):
        self.template_repository.init_repository()
        template = self.template_repository.create(
            t.Template(
                id=0,
                origin_file="test.html",
                creation_date=None,
                elements=[
                    t.Element(
                        id=0,
                        tag="div",
                        classes=["post", "post-wrapper"],
                        id_attr="post-1",
                        type=1
                    ),
                    t.Element(
                        id=0,
                        tag="div",
                        classes=["post-header"],
                        id_attr="post-header-1",
                        type=1
                    )
                ]
            )
        )
        self.assertIsNotNone(template)
        self.assertIsNotNone(template.id)
        self.assertEqual(template.origin_file, "test.html")
        self.assertEqual(len(template.elements), 2)

    def test_get_template_by_id(self):
        self.template_repository.init_repository()
        self._fill_db()
        template = self.template_repository.get_by_id(1)
        self.assertIsNotNone(template)
        self.assertEqual(template.id, 1)
        self.assertEqual(template.origin_file, "test.html")
        self.assertEqual(len(template.elements), 2)

    def test_delete_template(self):
        self.template_repository.init_repository()
        self._fill_db()
        self.template_repository.delete(1)
        templates = self.template_repository.get_all()
        self.assertEqual(len(templates), 0)

if __name__ == "__main__":
    unittest.main()