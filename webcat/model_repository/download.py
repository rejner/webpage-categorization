from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import AutoModelForTokenClassification
import sys
import os
import logging
logging.basicConfig(level=logging.INFO)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import WebCatNERPipeline (gets registered as pipeline, accesible via pipeline("webcat-ner"))
from webcat.nlp.models.ner.tweetner7 import WebCatNERPipeline

model_storage = "model_repository"

models = {
    "facebook/bart-large-mnli": {
        "tokenizer": "facebook/bart-large-mnli",
        "model": "facebook/bart-large-mnli",
        "pipeline": "zero-shot-classification",
        "model_class": AutoModelForSequenceClassification,
        "tokenizer_class": AutoTokenizer 
    },
    "tner/twitter-roberta-base-dec2021-tweetner7-random": {
        "tokenizer": "tner/twitter-roberta-base-dec2021-tweetner7-random",
        "model": "tner/twitter-roberta-base-dec2021-tweetner7-random",
        "pipeline": "webcat-ner",
        "model_class": AutoModelForTokenClassification,
        "tokenizer_class": AutoTokenizer
    },
}

for model_name, model_info in models.items():
    # test if model already exists
    if os.path.exists(os.path.join(model_storage, model_name)):
        logging.info(f"Model {model_name} already exists, skipping download.")
        # try to load model
        try:
            tokenizer = model_info["tokenizer_class"].from_pretrained(os.path.join(model_storage, model_name))
            model = model_info["model_class"].from_pretrained(os.path.join(model_storage, model_name))
            pipe = pipeline(model_info["pipeline"], model=model, tokenizer=tokenizer)
        except Exception as e:
            logging.error(f"Model {model_name} could not be loaded: {e}")
        
        finally:
            continue

    tokenizer = model_info["tokenizer_class"].from_pretrained(model_info["tokenizer"])
    model = model_info["model_class"].from_pretrained(model_info["model"])
    pipe = pipeline(model_info["pipeline"], model=model, tokenizer=tokenizer)
    pipe.save_pretrained(os.path.join(model_storage, model_name))
