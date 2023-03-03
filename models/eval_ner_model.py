import sys
sys.path.append("/workspaces/webpage_categorization")

import keras
import tensorflow as tf
import tensorflow_datasets as tfds
from metrics import custom_accuracy, entities_only_accuracy, calculate_ner_metrics
from losses import CustomNonPaddingTokenLoss
# from bert_preprocessing import preprocess_for_NER, NERTokenizerForBERT
from roberta_preprocessing import preprocess_for_NER, NERTokenizerForRoBERTa
from models.datasets.tweebank_ner.loader import TweebankNERLoader
from models.datasets.tweetner7.loader import Tweetner7Loader
from models.datasets.webcat_SDME.loader import WebCatSDMELoader

from data.entity_recognition_datasets.src.utils import *


if __name__ == "__main__":
    path = "/workspaces/webpage_categorization/models/checkpoints/my_ner_model__ro_ber_ta__last__four_lstm_20230224_093348"
    with keras.utils.custom_object_scope({'CustomNonPaddingTokenLoss': CustomNonPaddingTokenLoss,
                                        'custom_accuracy': custom_accuracy,
                                        'entities_only_accuracy': entities_only_accuracy}):
        # model = tf.keras.models.load_model(f"/workspaces/webpage_categorization/models/checkpoints/my_ner_model_20230213_180605")
        model = tf.keras.models.load_model(path)
    # tokenizer = NERTokenizerForBERT()
    tokenizer = NERTokenizerForRoBERTa()
    model.summary()

    # evaluate the model
    ds1 = tfds.load('conll2003', split='test')
    # ds2 = TweebankNERLoader().load('test')
    # ds1 = Tweetner7Loader().load('dev_random')
    # ds1 = WebCatSDMELoader().load('test')
    # ds = ds1.concatenate(ds2)
    ds = ds1

    # create conll2003 label mapping, but increse the number of labels by 1 and add a [PAD] label
    label_mapping = {0: "[PAD]", 1: "O", 2: "B-PER", 3: "I-PER", 4: "B-ORG", 5: "I-ORG", 6: "B-LOC", 7: "I-LOC", 8: "B-MISC", 9: "I-MISC", 10: "B-PROD", 11: "I-PROD", 12: "B-WALL"}
    

    ds = ds.apply(preprocess_for_NER)
    ds = ds.batch(128)

    # for example in ds.take(20):
    #     encoder_inputs = example[0]
    #     labels = example[1]
    #     out = model.predict(encoder_inputs)
        
    #     tokens = tokenizer.ids_to_tokens(encoder_inputs["input_word_ids"].numpy()[0])
    #     # argmax the output
    #     out = tf.argmax(out[0], axis=-1)
    #     out = out.numpy()
    #     labels_str = tokenizer.ids_to_labels(out)

    #     # remove [PAD] tokens which are after [SEP] token
    #     sep_index = tokens.index("[SEP]") + 1
    #     tokens = tokens[:sep_index]
    #     labels_str = labels_str[:sep_index]

    #     gt_labels_str = tokenizer.ids_to_labels(labels.numpy()[0])
    #     gt_labels_str = gt_labels_str[:sep_index]

    #     # print the results but align all printed elements
    #     # print header
    #     print(f"{'Token':<20} {'Pred':<10} {'GT':<10}")
    #     for i in range(len(tokens)):
    #         print(f"{tokens[i]:<20} {labels_str[i]:<10} {gt_labels_str[i]:<10}")
    #     print()

    # evaluate the model
    # loss, accuracy, entity_only_accuracy = model.evaluate(ds)
    # print(f"Loss: {loss}, Accuracy: {accuracy}, Entities only accuracy: {entity_only_accuracy}")
    calculate_ner_metrics(ds, model, label_mapping)




