import keras
import tensorflow as tf

# categorical crossentropy loss
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False, reduction="none")

# create dummy data of shape (32, 128)
y_true = tf.random.uniform(shape=(32, 128), minval=0, maxval=9, dtype=tf.int32)

# create dummy logits of shape (32, 128, 9) softmax over last axis
y_pred = tf.random.uniform(shape=(32, 128, 9), minval=0, maxval=1, dtype=tf.float32)


# input shapes: (32, 52) and logits.shape=(32, 128, 9)
# compute loss for each token

# pad true labels with -1
y_true = tf.pad(y_true, [[0, 0], [0, 128 - tf.shape(y_true)[1]]], constant_values=tf.constant(0, dtype=tf.int32))
y_true = tf.cast(y_true, dtype=tf.int32)
# argmax from pred to get the most probable class
#y_pred = tf.argmax(y_pred, axis=-1)
# convert y_pred to int32
#y_pred = tf.cast(y_pred, dtype=tf.int32)
#y_pred = tf.reshape(y_pred, (-1, 128))

loss = loss_fn(y_true, y_pred)
mask = tf.cast((y_true > 0), dtype=tf.float32)
loss = loss * mask
print(tf.reduce_sum(loss) / tf.reduce_sum(mask))


 