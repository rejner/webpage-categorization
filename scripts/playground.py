import tensorflow_hub as hub
import tensorflow as tf
import tensorflow_text as text

# Load BERT and the preprocessing model from TF Hub.
# https://tfhub.dev/tensorflow/bert_en_cased_L-12_H-768_A-12/4
# https://tfhub.dev/tensorflow/bert_en_cased_preprocess/3
#preprocess = hub.load('https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/1')
#encoder = hub.load('https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/3')

preprocess = hub.load('https://tfhub.dev/tensorflow/bert_en_cased_preprocess/3')
encoder = hub.load('https://tfhub.dev/tensorflow/bert_en_cased_L-12_H-768_A-12/4')

# Use BERT on a batch of raw text inputs.
input = preprocess(['Batch of inputs', 'TF Hub makes BERT easy!', 'More text.'])
pooled_output = encoder(input)["pooled_output"]
print(pooled_output)