import keras
import tensorflow as tf
import tensorflow_datasets as tfds
from train_ner_bert import CustomNonPaddingTokenLoss, custom_accuracy, entities_only_accuracy
from bert_preprocessing import preprocess_for_NER, NERTokenizerForBERT
import tensorflow_hub as hub

if __name__ == "__main__":
    with keras.utils.custom_object_scope({'CustomNonPaddingTokenLoss': CustomNonPaddingTokenLoss,
                                        'custom_accuracy': custom_accuracy,
                                        'entities_only_accuracy': entities_only_accuracy}):
        model = tf.keras.models.load_model(f"/workspaces/webpage_categorization/scripts/models/my_ner_model_20230213_180605")
    tokenizer = NERTokenizerForBERT()
    model.summary()
    # evaluate the model
    ds = tfds.load('conll2003', split='dev')

    # create conll2003 label mapping, but increse the number of labels by 1 and add a [PAD] label
    label_mapping = {0: "[PAD]", 1: "O", 2: "B-PER", 3: "I-PER", 4: "B-ORG", 5: "I-ORG", 6: "B-LOC", 7: "I-LOC", 8: "B-MISC", 9: "I-MISC"}
    
    ds = ds.apply(preprocess_for_NER)
    ds = ds.batch(1)

    for example in ds.take(20):
        encoder_inputs = example[0]
        labels = example[1]
        out = model.predict(encoder_inputs)
        
        tokens = tokenizer.ids_to_tokens(encoder_inputs["input_word_ids"].numpy()[0])
        # argmax the output
        out = tf.argmax(out[0], axis=-1)
        out = out.numpy()
        labels_str = tokenizer.ids_to_labels(out)

        # remove [PAD] tokens which are after [SEP] token
        sep_index = tokens.index("[SEP]") + 1
        tokens = tokens[:sep_index]
        labels_str = labels_str[:sep_index]

        gt_labels_str = tokenizer.ids_to_labels(labels.numpy()[0])
        gt_labels_str = gt_labels_str[:sep_index]

        # print the results but align all printed elements
        # print header
        print(f"{'Token':<20} {'Pred':<10} {'GT':<10}")
        for i in range(len(tokens)):
            print(f"{tokens[i]:<20} {labels_str[i]:<10} {gt_labels_str[i]:<10}")
        print()



