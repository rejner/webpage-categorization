import keras
import tensorflow as tf

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