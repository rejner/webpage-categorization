from .classification.bart_large_mnli import BARTLarge
from .classification.DeBERTa_v3_base_mnli import DeBerta_v3_base_mnli
from .classification.DeBERTa_v3_large_mnli import DeBerta_v3_large_mnli
from .ner.tweetner7 import TweetNER7, WebCatNERPipeline
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import AutoModelForTokenClassification

models = [
    {
        "tokenizer": "facebook/bart-large-mnli",
        "model": "facebook/bart-large-mnli",
        "pipeline": "zero-shot-classification",
        "model_class": AutoModelForSequenceClassification,
        "tokenizer_class": AutoTokenizer,
        "base_class": BARTLarge,
        "task": "classification",
        "default": True
    },
    {
        "tokenizer": "tner/twitter-roberta-base-dec2021-tweetner7-random",
        "model": "tner/twitter-roberta-base-dec2021-tweetner7-random",
        "pipeline": "webcat-ner",
        "model_class": AutoModelForTokenClassification,
        "tokenizer_class": AutoTokenizer,
        "base_class": TweetNER7,
        "task": "ner",
        "default": True
    },
    {
        "tokenizer": "MoritzLaurer/DeBERTa-v3-base-mnli",
        "model": "MoritzLaurer/DeBERTa-v3-base-mnli",
        "pipeline": "zero-shot-classification",
        "model_class": AutoModelForSequenceClassification,
        "tokenizer_class": AutoTokenizer,
        "base_class": DeBerta_v3_base_mnli,
        "task": "classification",
        "default": False
    },
    {
        "tokenizer": "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
        "model": "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
        "pipeline": "zero-shot-classification",
        "model_class": AutoModelForSequenceClassification,
        "tokenizer_class": AutoTokenizer,
        "base_class": DeBerta_v3_large_mnli,
        "task": "classification",
        "default": False
    }
]


def list_classification_models():
    classification_models = []
    for model in models:
        if models["task"] == "classification":
            classification_models.append(model)
    return classification_models



def list_ner_models():
    ner_models = []
    for model in models:
        if models["task"] == "ner":
            ner_models.append(model)
    return ner_models

def list_all_models():
    return models