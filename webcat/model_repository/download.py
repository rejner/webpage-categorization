import sys
import os
import logging
logging.basicConfig(level=logging.INFO)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from webcat.nlp.models import list_all_models
from transformers import pipeline


model_storage = "/workspace/webcat/model_repository"
models = list_all_models()

for model in models:
    # test if model already exists
    if os.path.exists(os.path.join(model_storage, model['model'])):
        logging.info(f"Model {model['model']} already exists, skipping download.")
        # try to load model
        try:
            tokenizer = model["tokenizer_class"].from_pretrained(os.path.join(model_storage, model['model']))
            model = model["model_class"].from_pretrained(os.path.join(model_storage, model['model']))
            pipe = pipeline(model["pipeline"], model=model, tokenizer=tokenizer)
        except Exception as e:
            logging.error(f"Model {model['model']} could not be loaded: {e}")
        
        finally:
            continue
    
    logging.info(f"Downloading model {model['model']}")
    logging.info(f"Path: {model['model']}")

    tokenizer = model["tokenizer_class"].from_pretrained(model["tokenizer"])
    model = model["model_class"].from_pretrained(model["model"])
    pipe = pipeline(model["pipeline"], model=model, tokenizer=tokenizer)
    pipe.save_pretrained(os.path.join(model_storage, model['model']))
