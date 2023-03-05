import sys
from os import path
sys.path.append(path.dirname(__file__) + "/..")
from models.classification.joeddav_xlm_roberta import XLMRobertaLarge
from models.ner.tweetner7 import TweetNER7

'''
    Analyzer class definition.
'''
class WebCatAnalyzer():
    def __init__(self):
        self.classifier = XLMRobertaLarge()
        self.ner_model = TweetNER7()

    def analyze_content(self, content, **kwargs):
        categories = self.classify(content, **kwargs)
        entities, text = self.perform_NER(content, **kwargs)
        return categories, entities, text
    
    def classify(self, inputs, **kwargs):
        inputs = self.verify_inputs(inputs)
        categories = self.classifier.classify(inputs, **kwargs)
        return categories
    
    def perform_NER(self, inputs, **kwargs):
        inputs = self.verify_inputs(inputs)
        entities, text = self.ner_model.classify(inputs)
        return entities, text
    
    def verify_inputs(self, inputs):
        if not isinstance(inputs, list):
            inputs = [inputs]
        assert len(inputs[0]) > 0, "No inputs provided"
        assert isinstance(inputs[0], str), "Inputs must be strings"
        return inputs


    
