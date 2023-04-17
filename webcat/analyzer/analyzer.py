import sys
from os import path
sys.path.append(path.dirname(__file__) + "/..")
from .models.classification.joeddav_xlm_roberta import XLMRobertaLarge
from .models.classification.bart_large_mnli import BARTLarge
from .models.classification.DeBERTa_v3_base_mnli import DeBerta_v3_base_mnli
from .models.ner.tweetner7 import TweetNER7
import logging
from .models import list_all_models

'''
    Analyzer class definition.
'''
class WebCatAnalyzer():
    def __init__(self, models=None):
        # self.classifier = XLMRobertaLarge()
        # self.classifier = BARTLarge()
        self.init_models(models)
           
    def init_models(self, models):
        if models is None:
            self.classifier = BARTLarge()
            self.ner_model = TweetNER7()
        else:
            available_models = list_all_models()
            # init classification mode
            name = models['classification']
            for model in available_models:
                if model['base_class'].name == name:
                    self.classifier = model['base_class']()
            
            # init ner model
            name = models['ner']
            for model in available_models:
                if model['base_class'].name == name:
                    self.ner_model = model['base_class']()
        
        logging.info("""
        Initialized WebCatAnalyzer with the following models:
        Classification: {}
        NER: {}
        """.format(self.classifier.name, self.ner_model.name))

    def analyze_content(self, content, **kwargs):
        try:
            categories = self.classify(content, **kwargs)
            logging.info(categories)
            entities, text = self.perform_NER(content, **kwargs)
            logging.info(entities)
            return categories, entities, text
        except Exception as e:
            print(e)
            return None, None, None
    
    def analyze_dataset(self, dataset, **kwargs):
        try:
            logging.info("Analyzing dataset")
            logging.info("Classifying dataset")
            categories = self.classify_dataset(dataset, **kwargs)
            logging.info("Performing NER on dataset")
            entities, text = self.perform_NER_dataset(dataset, **kwargs)
            logging.info("Finished analyzing dataset")
            return categories, entities, text
        except Exception as e:
            print(e.with_traceback(None))
            return None, None, None
        
    def classify(self, inputs, **kwargs):
        # inputs = self.verify_inputs(inputs)
        categories = self.classifier.classify(inputs, **kwargs)
        return categories
    
    def perform_NER(self, inputs, **kwargs):
        # inputs = self.verify_inputs(inputs)
        entities, text = self.ner_model.classify(inputs)
        return entities, text
    
    def classify_dataset(self, dataset, **kwargs):
        # inputs = self.verify_inputs(inputs)
        categories = self.classifier.classify_dataset(dataset, **kwargs)
        return categories
    
    def perform_NER_dataset(self, dataset, **kwargs):
        # inputs = self.verify_inputs(inputs)
        entities, text = self.ner_model.classify_dataset(dataset)
        return entities, text
    
    def verify_inputs(self, inputs):
        if not isinstance(inputs, list):
            inputs = [inputs]
        assert len(inputs[0]) > 0, "No inputs provided"
        assert isinstance(inputs[0], str), "Inputs must be strings (is list of {})".format(type(inputs[0]))
        return inputs


    
