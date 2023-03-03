import tensorflow as tf
import numpy as np
from conlleval import evaluate

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

def calculate_ner_metrics(dataset, ner_model, mapping):
    all_true_tag_ids, all_predicted_tag_ids = [], []

    for x, y in dataset:
        output = ner_model.predict(x)
        predictions = np.argmax(output, axis=-1)
        predictions = np.reshape(predictions, [-1])

        true_tag_ids = np.reshape(y, [-1])

        mask = (true_tag_ids > 0) & (predictions > 0)
        true_tag_ids = true_tag_ids[mask]
        predicted_tag_ids = predictions[mask]

        all_true_tag_ids.append(true_tag_ids)
        all_predicted_tag_ids.append(predicted_tag_ids)

    all_true_tag_ids = np.concatenate(all_true_tag_ids)
    all_predicted_tag_ids = np.concatenate(all_predicted_tag_ids)

    predicted_tags = [mapping[tag] for tag in all_predicted_tag_ids]
    real_tags = [mapping[tag] for tag in all_true_tag_ids]

    evaluate(real_tags, predicted_tags)