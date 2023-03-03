import sys
sys.path.append("/workspaces/webpage_categorization")

import tensorflow as tf
import tensorflow_datasets as tfds
import tensorflow_text as text
import keras
from datetime import datetime
from roberta_preprocessing import preprocess_for_NER
from architectures.my_ner_model import MyNERModel_RoBERTa_Last_Four_LSTM, MyNERModel_RoBERTa_LSTM
from losses import CustomNonPaddingTokenLoss
from metrics import custom_accuracy, entities_only_accuracy
from keras.callbacks import ModelCheckpoint, EarlyStopping
from models.datasets.tweebank_ner.loader import TweebankNERLoader
from models.datasets.BTC.loader import BTCLoader
from models.datasets.tweetner7.loader import Tweetner7Loader
from models.datasets.webcat_SDME.loader import WebCatSDMELoader

def load_datasets(datasets=['conll2003', 'tweebank_ner'], split='train'):
    ds = None
    # iterate over all datasets and concatenate them
    for dataset in datasets:
        if dataset == 'conll2003':
            ds_tmp = tfds.load('conll2003', split=split).apply(preprocess_for_NER)
        elif dataset == 'tweebank_ner':
            ds_tmp = TweebankNERLoader().load(split).apply(preprocess_for_NER)
        elif dataset == 'BTC':
            ds_tmp = BTCLoader().load(split).apply(preprocess_for_NER)
        elif dataset == 'tweetner7':
            ds_tmp = Tweetner7Loader().load(split).apply(preprocess_for_NER)
        elif dataset == 'webcat_SDME':
            ds_tmp = WebCatSDMELoader().load(split).apply(preprocess_for_NER)
        else:
            raise Exception(f"Unknown dataset: {dataset}")
        if ds is None:
            ds = ds_tmp
        else:
            ds = ds.concatenate(ds_tmp)
    return ds

if __name__ == "__main__":
    # ds = tfds.load('conll2003', split='train').apply(preprocess_for_NER).batch(64).shuffle(64).prefetch(tf.data.experimental.AUTOTUNE)
    # ds_dev = tfds.load('conll2003', split='dev').apply(preprocess_for_NER).batch(64).prefetch(tf.data.experimental.AUTOTUNE)

    datasets = ['conll2003']

    ds = load_datasets(datasets=datasets, split='train').batch(32).prefetch(tf.data.experimental.AUTOTUNE)
    ds_dev = load_datasets(datasets=datasets, split='dev').batch(32).prefetch(tf.data.experimental.AUTOTUNE)

    # create a custom loss function
    loss_fn = CustomNonPaddingTokenLoss()

    # define callbacks
    checkpoint = ModelCheckpoint("/workspaces/webpage_categorization/models/tmp/checkpoint/checkpoint", save_weights_only=True, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
    early = EarlyStopping(monitor="val_loss", mode="min", patience=2)

    # create a custom model
    # model = MyNERModel(num_classes=9+1)
    # model = MyNERModel_RoBERTa_LSTM(num_classes=9+1)
    model = MyNERModel_RoBERTa_LSTM(num_classes=12+1)

    optimizer = tf.keras.optimizers.Adam(learning_rate=2e-5)
    model.compile(optimizer="adam", loss=loss_fn, metrics=[custom_accuracy, entities_only_accuracy])

    # train the model
    history = model.fit(ds, epochs=10, validation_data=ds_dev, callbacks=[early, checkpoint])

    # print the history
    print(history.history)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model.save(f"/workspaces/webpage_categorization/models/checkpoints/{model.name}_{timestamp}")
    print(f"Model saved to /workspaces/webpage_categorization/models/checkpoints/{model.name}_{timestamp}.")

    # evaluate the model
    # ds = tfds.load('conll2003', split='test').apply(preprocess_for_NER).batch(64).prefetch(tf.data.experimental.AUTOTUNE)
    ds = load_datasets(datasets=datasets, split='test').batch(64).prefetch(tf.data.experimental.AUTOTUNE)

    with keras.utils.custom_object_scope({'CustomNonPaddingTokenLoss': CustomNonPaddingTokenLoss,
                                          'custom_accuracy': custom_accuracy,
                                          'entities_only_accuracy': entities_only_accuracy}):
        model = tf.keras.models.load_model(f"/workspaces/webpage_categorization/models/checkpoints/{model.name}_{timestamp}")
    model.evaluate(ds)
