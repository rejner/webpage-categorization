import tensorflow as tf
import tensorflow_datasets as tfds
import tensorflow_hub as hub
import tensorflow_text as text
import keras
import numpy as np
from datetime import datetime
from bert_preprocessing import preprocess_for_NER

class CustomNonPaddingTokenLoss(keras.losses.Loss):
    def __init__(self, name="custom_ner_loss", **kwargs):
        super().__init__(name=name)
        self.loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)

    def call(self, y_true, y_pred):
        # input shapes: (32, 52) and logits.shape=(32, 128, 9)
        # compute loss for each token
        loss = self.loss_fn(y_true, y_pred)
        mask = tf.cast((y_true > 0), dtype=tf.float32)
        loss = loss * mask
        return tf.reduce_sum(loss) / tf.reduce_sum(mask)

# create custom accuracy metric
def custom_accuracy(y_true, y_pred):
    # input shapes: (32, 52) and logits.shape=(32, 128, 9)
    # compute loss for each token
    y_true = tf.cast(y_true, dtype=tf.int32)
    y_pred = tf.argmax(y_pred, axis=-1)
    y_pred = tf.cast(y_pred, dtype=tf.int32)
    mask = tf.cast((y_true > 0), dtype=tf.float32)

    correct = tf.cast(tf.equal(y_true, y_pred), dtype=tf.float32)
    correct = correct * mask
    return tf.reduce_sum(correct) / tf.reduce_sum(mask)

def entities_only_accuracy(y_true, y_pred):
    # input shapes: (32, 52) and logits.shape=(32, 128, 9)
    # compute loss for each token
    y_true = tf.cast(y_true, dtype=tf.int32)
    y_pred = tf.argmax(y_pred, axis=-1)
    y_pred = tf.cast(y_pred, dtype=tf.int32)
    mask = tf.cast((y_true > 1), dtype=tf.float32)

    correct = tf.cast(tf.equal(y_true, y_pred), dtype=tf.float32)
    correct = correct * mask
    return tf.reduce_sum(correct) / tf.reduce_sum(mask)
    


class MyNERModel(keras.Model):
    def __init__(self, num_classes, **kwargs):
        super().__init__(**kwargs)
        # use pre-trained BERT model
        self.bert = hub.KerasLayer(
            "https://tfhub.dev/tensorflow/bert_en_cased_L-12_H-768_A-12/4",
        trainable=False)

        self.dropout = keras.layers.Dropout(0.1)
        self.classifier = keras.layers.Dense(num_classes, activation="softmax")
        """
        self.lstm = keras.layers.Bidirectional(
            keras.layers.LSTM(
                units=128,
                return_sequences=True
            )
        )
        """
        # create a dense layer for each token
        classification_head = keras.Sequential([
            keras.layers.Dense(512, activation="relu"),
            keras.layers.Dense(num_classes, activation="softmax")
        ])
        self.classifier = keras.layers.TimeDistributed(
            classification_head
        )

    def call(self, inputs):
        bert_output = self.bert(inputs)
        # now classify the output for each token
        # output = self.lstm(bert_output["sequence_output"])
        output = bert_output["sequence_output"]
        output = self.dropout(output, training=False)
        output = self.classifier(output)
        return output

if __name__ == "__main__":
    ds = tfds.load('conll2003', split='train')

    ds_dev = tfds.load('conll2003', split='dev')
    ds_dev = ds_dev.apply(preprocess_for_NER)
    ds_dev = ds_dev.padded_batch(256)
    ds_dev = ds_dev.prefetch(tf.data.experimental.AUTOTUNE)

    # create a custom loss function
    loss_fn = CustomNonPaddingTokenLoss()

    # create a custom model
    model = MyNERModel(num_classes=9+1)
    model.compile(optimizer="adam", loss=loss_fn, metrics=[custom_accuracy, entities_only_accuracy])

    ds = ds.apply(preprocess_for_NER)
    ds = ds.batch(128)
    # shuffle the dataset
    ds = ds.shuffle(100)
    ds = ds.prefetch(tf.data.experimental.AUTOTUNE)


    # train the model
    model.fit(ds, epochs=10, validation_data=ds_dev)
    # save the model
    # model.predict(ds.take(1))
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model.save(f"scripts/models/my_ner_model_{timestamp}")

    # evaluate the model
    ds = tfds.load('conll2003', split='test')
    ds = ds.apply(preprocess_for_NER)
    ds = ds.padded_batch(128)
    ds = ds.prefetch(tf.data.experimental.AUTOTUNE)

    with keras.utils.custom_object_scope({'CustomNonPaddingTokenLoss': CustomNonPaddingTokenLoss,
                                          'custom_accuracy': custom_accuracy,
                                          'entities_only_accuracy': entities_only_accuracy}):
        model = tf.keras.models.load_model(f"scripts/models/my_ner_model_{timestamp}")
    model.evaluate(ds)
