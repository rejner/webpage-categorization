import keras
import tensorflow_hub as hub
import tensorflow as tf

class MyNERModel(keras.Model):
    def __init__(self, num_classes, name="MyNERModel", **kwargs):
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

class MyNERModel_BERT_LSTM(keras.Model):
    def __init__(self, num_classes, name="MyNERModel_BERT_LSTM", **kwargs):
        super().__init__(**kwargs)
        # use pre-trained BERT model
        self.bert = hub.KerasLayer(
            "https://tfhub.dev/tensorflow/bert_en_cased_L-12_H-768_A-12/4",
        trainable=False)
        # self.bert = hub.KerasLayer(
        #     "https://tfhub.dev/tensorflow/bert_en_cased_L-24_H-1024_A-16/4",
        # trainable=False
        # )

        self.dropout = keras.layers.Dropout(0.1)
        self.classifier = keras.layers.Dense(num_classes, activation="softmax")
        self.lstm = keras.layers.Bidirectional(
            keras.layers.LSTM(
                units=256,
                return_sequences=True
            )
        )

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
        output = self.lstm(output)
        output = self.classifier(output)
        return output

class MyNERModel_BERT_Last_Four_LSTM(keras.Model):
    def __init__(self, num_classes, name="MyNERModel_BERT_Last_Four_LSTM", **kwargs):
        super().__init__(**kwargs)
        # use pre-trained BERT model
        self.bert = hub.KerasLayer(
            "https://tfhub.dev/tensorflow/bert_en_cased_L-12_H-768_A-12/4",
        trainable=False)
        # self.bert = hub.KerasLayer(
        #     "https://tfhub.dev/tensorflow/bert_en_cased_L-24_H-1024_A-16/4",
        # trainable=False
        # )

        self.dropout = keras.layers.Dropout(0.1)
        self.classifier = keras.layers.Dense(num_classes, activation="softmax")
        # Create two layers of LSTM with 768 units each
        self.lstm = keras.layers.Bidirectional(
            keras.layers.LSTM(
                units=768,
                return_sequences=True
            )
        )

        # create a dense layer for each token
        classification_head = keras.Sequential([
            keras.layers.Dense(1024, activation="relu", kernel_regularizer=keras.regularizers.l2(0.01)),
            keras.layers.Dense(num_classes, activation="softmax")
        ])
        self.classifier = keras.layers.TimeDistributed(
            classification_head
        )

    def call(self, inputs):
        bert_output = self.bert(inputs)
        # now classify the output for each token
        encoder_output = bert_output["encoder_outputs"]
        # get the last four layers
        last_four_layers = encoder_output[-4:]
        # concatenate the last four layers
        last_four_layers = tf.concat(last_four_layers, axis=-1)
        # now classify the output for each token
        output = self.dropout(last_four_layers, training=False)
        output = self.lstm(output)
        output = self.classifier(output)
        return output

class MyNERModel_RoBERTa_Last_Four_LSTM(keras.Model):
    def __init__(self, num_classes, name="MyNERModel_RoBERTa_Last_Four_LSTM", **kwargs):
        super().__init__(**kwargs)
        # use pre-trained BERT model
        self.bert = hub.KerasLayer(
            "https://tfhub.dev/jeongukjae/roberta_en_cased_L-12_H-768_A-12/1",
        trainable=False)
        # self.bert = hub.KerasLayer(
        #     "https://tfhub.dev/tensorflow/bert_en_cased_L-24_H-1024_A-16/4",
        # trainable=False
        # )

        self.dropout = keras.layers.Dropout(0.1)
        self.classifier = keras.layers.Dense(num_classes, activation="softmax")
        # Create two layers of LSTM with 768 units each
        self.lstm = keras.layers.Bidirectional(
            keras.layers.LSTM(
                units=768,
                return_sequences=True
            )
        )

        # create a dense layer for each token
        classification_head = keras.Sequential([
            keras.layers.Dense(1024, activation="relu"),
            keras.layers.Dense(num_classes, activation="softmax")
        ])
        self.classifier = keras.layers.TimeDistributed(
            classification_head
        )

    def call(self, inputs):
        bert_output = self.bert(inputs)
        # now classify the output for each token
        encoder_output = bert_output["encoder_outputs"]
        # get the last four layers
        last_four_layers = encoder_output[-4:]
        # concatenate the last four layers
        last_four_layers = tf.concat(last_four_layers, axis=-1)
        # now classify the output for each token
        output = self.dropout(last_four_layers, training=False)
        output = self.lstm(output)
        output = self.classifier(output)
        return output

class MyNERModel_RoBERTa_LSTM(keras.Model):
    def __init__(self, num_classes, name="MyNERModel_RoBERTa_LSTM", **kwargs):
        super().__init__(**kwargs)
        # use pre-trained BERT model
        self.bert = hub.KerasLayer(
            "https://tfhub.dev/jeongukjae/roberta_en_cased_L-24_H-1024_A-16/1",
        trainable=False)
        # self.bert = hub.KerasLayer(
        #     "https://tfhub.dev/tensorflow/bert_en_cased_L-24_H-1024_A-16/4",
        # trainable=False
        # )

        self.dropout = keras.layers.Dropout(0.1)
        self.classifier = keras.layers.Dense(num_classes, activation="softmax")
        # Create two layers of LSTM with 768 units each
        self.lstm = keras.layers.Bidirectional(
            keras.layers.LSTM(
                units=768,
                return_sequences=True
            )
        )

        # create a dense layer for each token
        classification_head = keras.Sequential([
            keras.layers.Dense(1024, activation="relu"),
            keras.layers.Dense(num_classes, activation="softmax")
        ])
        self.classifier = keras.layers.TimeDistributed(
            classification_head
        )

    def call(self, inputs):
        bert_output = self.bert(inputs)
        # now classify the output for each token
        encoder_output = bert_output["sequence_output"]
        # now classify the output for each token
        output = self.dropout(encoder_output, training=False)
        output = self.lstm(output)
        output = self.classifier(output)
        return output

if __name__ == "__main__":
    # model = MyNERModel_BERT_Last_Four_LSTM(3)
    model = MyNERModel_RoBERTa_Last_Four_LSTM(3)

    # test the model
    # dummy data
    input_ids = tf.constant([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10] + [0] * 246])
    input_mask = tf.constant([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1] + [1] * 246])
    segment_ids = tf.constant([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0] + [0] * 246])
    encoder_inputs = {
        "input_word_ids": input_ids,
        "input_mask": input_mask,
        "input_type_ids": segment_ids
    }
    output = model(encoder_inputs)
    print(output)


