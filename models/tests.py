from train_ner_bert import custom_accuracy
import unittest
import tensorflow as tf


class TestCustomAccuracy(unittest.TestCase):
    
    def test_a(self):
        # create dummy data of shape (2, 5) for gt and (2, 5, 3) for logits
        # labels can be 0, 1 and 2 values only
        y_true = tf.constant([[0, 1, 2, 0, 1], [0, 1, 2, 0, 1]])
        y_pred = tf.constant([[[0.9, 0.05, 0.05], [0.05, 0.9, 0.05], [0.05, 0.05, 0.9], [0.9, 0.05, 0.05], [0.05, 0.9, 0.05]],
                              [[0.9, 0.05, 0.05], [0.05, 0.9, 0.05], [0.05, 0.05, 0.9], [0.9, 0.05, 0.05], [0.05, 0.9, 0.05]]])
        # compute accuracy
        acc = custom_accuracy(y_true, y_pred)
        self.assertEqual(acc, 1.0)

    def test_b(self):
        # create dummy data of shape (2, 5) for gt and (2, 5, 3) for logits
        # labels can be 0, 1 and 2 values only
        y_true = tf.constant([[0, 1, 2, 0, 1], [0, 1, 2, 0, 1]])
        y_pred = tf.constant([[[0.9, 0.05, 0.05], [0.05, 0.05, 0.9], [0.05, 0.05, 0.9], [0.9, 0.05, 0.05], [0.05, 0.9, 0.05]], 
                              [[0.9, 0.05, 0.05], [0.05, 0.9, 0.05], [0.05, 0.05, 0.9], [0.9, 0.05, 0.05], [0.05, 0.9, 0.05]]])
        # compute accuracy
        acc = custom_accuracy(y_true, y_pred)
        self.assertEqual(acc, 5/6)
    
    def test_c(self):
        # create dummy data of shape (2, 5) for gt and (2, 5, 3) for logits
        # labels can be 0, 1 and 2 values only
        y_true = tf.constant([[0, 1, 1, 0, 1], [0, 1, 1, 0, 1]])
        # predictions are all wrong
        y_pred = tf.constant([[[0.05, 0.9, 0.05], [0.05, 0.05, 0.9], [0.05, 0.05, 0.9], [0.05, 0.9, 0.05], [0.05, 0.05, 0.9]],
                              [[0.05, 0.9, 0.05], [0.05, 0.05, 0.9], [0.05, 0.05, 0.9], [0.05, 0.9, 0.05], [0.05, 0.05, 0.9]]])

        # compute accuracy
        acc = custom_accuracy(y_true, y_pred)
        self.assertEqual(acc, 0/6)

if __name__ == "__main__":
    unittest.main()

