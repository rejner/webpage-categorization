import sys
from os import path
sys.path.append(path.dirname(__file__) + "/..")
import unittest
from webcat.analyzer.analyzer import WebCatAnalyzer
from webcat.constants import dummy_corpus

class TestAnalyzer(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.analyzer = WebCatAnalyzer()
        self.default_labels = ["drugs", "hacking", "fraud", "counterfeit goods", "cybercrime", "cryptocurrency"]

    def test_classification(self):
        text = dummy_corpus[0]
        categories = self.analyzer.classify(text)[0]
        self.assertIsInstance(categories, dict)
        self.assertEqual(len(categories.keys()), len(self.default_labels))
        for label in self.default_labels:
            self.assertIn(label, categories.keys())

    def test_classification_custom_labels(self):
        text = dummy_corpus[0]
        custom_labels = ["drugs", "sport", "politics"]
        categories = self.analyzer.classify(text, labels=custom_labels)[0]
        self.assertIsInstance(categories, dict)
        self.assertEqual(len(categories.keys()), len(custom_labels))
        for label in custom_labels:
            self.assertIn(label, categories.keys())
    
    def test_classification_multi_input(self):
        text = dummy_corpus[:3]
        categories = self.analyzer.classify(text)
        self.assertIsInstance(categories, list)
        self.assertEqual(len(categories), len(text))
        for category in categories:
            self.assertIsInstance(category, dict)
            self.assertEqual(len(category.keys()), len(self.default_labels))
            for label in self.default_labels:
                self.assertIn(label, category.keys())
    
    def test_ner(self):
        text = dummy_corpus[0]
        entities, text = self.analyzer.perform_NER(text)
        entities, text = entities[0], text[0]
        self.assertIsInstance(entities, list)
        self.assertIsInstance(text, str)
        self.assertGreater(len(entities), 0)
        self.assertGreater(len(text), 0)



if __name__ == "__main__":
    unittest.main()