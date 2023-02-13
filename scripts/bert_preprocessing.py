import keras
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import tensorflow_datasets as tfds

class NERTokenizerForBERT(keras.layers.Layer):
    """
    Tokenizer for BERT model
    The data from dataset is in the format of:
    {
        'tokens': [token1, token2, ...],
        'ner': [label1, label2, ...]
    }
    Tokens must be preprocessed before feeding into BERT model.
    Also, the labels must be adjusted to the new tokens after preprocessing.
    """
    def __init__(self, **kwargs):
        super(NERTokenizerForBERT, self).__init__(**kwargs)
        self.preprocess = hub.load('https://tfhub.dev/tensorflow/bert_en_cased_preprocess/3')
        self.tokenizer = hub.KerasLayer(self.preprocess.tokenize)
        self.bert_pack_inputs = hub.KerasLayer(self.preprocess.bert_pack_inputs, arguments=dict(seq_length=128))
        self.vocab_file = 'vocab.txt'
        self.max_seq_length = 128
        self.special_tokens_dict = self.preprocess.tokenize.get_special_tokens_dict()
        self.label_mapping = {0: "[PAD]", 1: "O", 2: "B-PER", 3: "I-PER", 4: "B-ORG", 5: "I-ORG", 6: "B-LOC", 7: "I-LOC", 8: "B-MISC", 9: "I-MISC"}
        self.load_vocab()

    def load_vocab(self):
        # create a vocabulary as dictionary
        with open(self.vocab_file, "r") as f:
            vocab = f.read()
        vocab = vocab.split("\n")
        vocab = vocab[:-1]
        self.vocab = {i: vocab[i] for i in range(len(vocab))}
        self.vocab_size = len(self.vocab)

    def id_to_token(self, id):
        return self.vocab[id]
    
    def ids_to_tokens(self, ids):
        return [self.id_to_token(id) for id in ids]
    
    def id_to_label(self, id):
        return self.label_mapping[id]
    
    def ids_to_labels(self, ids):
        return [self.id_to_label(id) for id in ids]
    
    @tf.function
    def call(self, inputs):
        words, word_labels = inputs
        word_labels += 1
        # use tf collections to store the labels
        # labels = [tf.constant([0], dtype=tf.int64)]
        labels = tf.constant([0], dtype=tf.int64)

        # make sure both words and word_labels are tensors of size not greater than 128
        # size of words
        # words = tf.slice(words, [0], [size_min])
        size = tf.shape(words)[0]
        tokenized_inputs_orig = self.tokenizer(words)
        tokenized_inputs = tokenized_inputs_orig.values
        

        # first dimention of world_labels match the number of words
        # extend the first dimension of word_labels to match the number of tokens
        # number of tokens can be different from number of words
        word_labels = tf.expand_dims(word_labels, axis=1)
        word_labels = tf.cast(word_labels, tf.int64)
        # initialize the loop variable
        i = tf.constant(0)
        
        # define the loop body
        def loop_body(i, labels):
            # get the number of tokens for the current word
            shape = tf.shape(tokenized_inputs_orig[i])
            # s = tf.constant(shape.inner_shape[0], dtype=tf.int32)
            # num_tokens = s._static_inner_shape[0]
            # extend the first dimension of word_labels to match the number of tokens
            word_label = tf.tile(word_labels[i], [shape.inner_shape[0]])
            # append the labels to the list
            labels = tf.concat([labels, word_label], axis=0)
            # increment the loop variable
            i += 1
            return i, labels
        
        # run the while loop
        i, labels = tf.while_loop(
            lambda i, labels: i < size, 
            loop_body, 
            [i, labels], 
            shape_invariants=[i.get_shape(), tf.TensorShape([None])]
        )

        # size_min = tf.minimum(i, self.max_seq_length)
        # word_labels = tf.slice(word_labels, [0], [size_min])
        # # append the last label
        # if size_min < self.max_seq_length:
        labels = tf.concat([labels, tf.constant([0], dtype=tf.int64)], axis=0)

        # cast labels to int32
        labels = tf.cast(labels, dtype=tf.int32)
        # calculate maximum of (self.max_seq_length - tf.shape(labels)[0]) and 0
        padding_offset = tf.maximum(self.max_seq_length - tf.shape(labels)[0], 0)

        # pad the labels to match the max_seq_length 
        labels = tf.pad(labels, [[0, padding_offset]], constant_values=0)
        
        tokenized_inputs = tf.expand_dims(tokenized_inputs, axis=0)
        encoder_inputs = self.bert_pack_inputs([tokenized_inputs])
        return encoder_inputs, labels

    def get_config(self):
        config = super().get_config().copy()
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)

def preprocess_for_NER(ds):
    tokenizer = NERTokenizerForBERT()

    @tf.function
    def preprocess(example):
        test_input = example['tokens']
        test_label = example['ner']
        inputs, labels = tokenizer((test_input, test_label))
        # squeeze dimension of keys
        for key in inputs.keys():
            inputs[key] = tf.squeeze(inputs[key], axis=0)
        
        if tf.shape(labels)[0] >= 128:
            labels = labels[:127]
            labels = tf.concat([labels, tf.constant([0], dtype=tf.int32)], axis=0)

        return inputs, labels

    return ds.map(preprocess)

def run_test_mode(ds):
    tokenizer = NERTokenizerForBERT()

    def preprocess(example):
        test_input = example['tokens']
        test_label = example['ner']
        inputs, labels = tokenizer((test_input, test_label))
        # squeeze dimension of keys
        for key in inputs.keys():
            inputs[key] = tf.squeeze(inputs[key], axis=0)
        
        if tf.shape(labels)[0] >= 128:
            labels = labels[:127]
            labels = tf.concat([labels, tf.constant([0], dtype=tf.int32)], axis=0)

        return inputs, labels
    
    for i, example in enumerate(ds):
        example_tokens = example['tokens'].numpy()
        # decode the bytes to string
        example_tokens = [token.decode('utf-8') for token in example_tokens]
        example_tokens = ['[CLS]'] + example_tokens + ['[SEP]']
        example_labels = example['ner'].numpy()
        example_labels += 1
        # predend the first label with 'O'
        example_labels = [0] + example_labels.tolist()
        example_labels = example_labels + [0]
        example_labels = [tokenizer.id_to_label(id) for id in example_labels]

        # print(f"{'Example':<20} {'GT':<10}")
        # for i in range(len(example_tokens)):
        #     print(f"{example_tokens[i]:<20} {example_labels[i]:<10}")
        # print()


        
        encoder_inputs, labels = preprocess(example)

        tokens = tokenizer.ids_to_tokens(encoder_inputs["input_word_ids"].numpy())
        sep_index = tokens.index("[SEP]") + 1
        tokens = tokens[:sep_index]
        gt_labels_str = tokenizer.ids_to_labels(labels.numpy())
        gt_labels_str = gt_labels_str[:sep_index]



        print(f"{'Token':<20} {'GT':<10} {'Example':<20} {'GT':<10}")
        for i in range(len(tokens)):
            if i < len(example_tokens):
                print(f"{tokens[i]:<20} {gt_labels_str[i]:<10} {example_tokens[i]:<20} {example_labels[i]:<10}")
            else:
                print(f"{tokens[i]:<20} {gt_labels_str[i]:<10}")
        
        print()


if __name__ == "__main__":
    
    ds = tfds.load('conll2003', split='train')
    # ds = tfds.as_dataframe(ds)
    tokenizer = NERTokenizerForBERT()

    # ds_test = ds.take(10)
    # run_test_mode(ds_test)
    # exit(0)
    
    # apply preprocess to each row of the dataframe
    ds = ds.apply(preprocess_for_NER)
    ds = ds.prefetch(100)

    for example in ds:
        encoder_inputs = example[0]
        labels = example[1]
        tokens = tokenizer.ids_to_tokens(encoder_inputs["input_word_ids"].numpy())
        assert len(tokens) == len(labels), f"tokens and labels must have the same length ({len(tokens)} != {len(labels)}))"
        pad_removed = [token for token in tokens if token != "[PAD]"]
        assert pad_removed[-1] == "[SEP]"
        assert tokens[0] == "[CLS]"
        assert labels[0] == 0
        assert labels[-1] == 0
        print(tokens[:16])
        labels = tokenizer.ids_to_labels(labels.numpy())
        print(labels[:16])
        print()

