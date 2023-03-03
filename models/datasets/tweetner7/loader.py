import sys
import os
import json
import tensorflow as tf
sys.path.append("/workspaces/webpage_categorization")

from models.datasets.loader_interace import DatasetLoaderInterface, Split, id_to_label_mapping, label_to_id_mapping

tweetner_mapping = {"B-corporation": 0, "B-creative_work": 1, "B-event": 2, "B-group": 3, "B-location": 4, "B-person": 5, "B-product": 6,
                    "I-corporation": 7, "I-creative_work": 8, "I-event": 9, "I-group": 10, "I-location": 11, "I-person": 12, "I-product": 13, "O": 14}
tweetner_to_dataset_mapping = {0: "B-ORG", 1: "B-MISC", 2: "B-MISC", 3: "B-ORG", 4: "B-LOC", 5: "B-PER", 6: "B-PROD",
                               7: "I-ORG", 8: "I-MISC", 9: "I-MISC", 10: "I-ORG", 11: "I-LOC", 12: "I-PER", 13: "I-PROD", 14: "O"}

class Tweetner7Loader(DatasetLoaderInterface):
    def __init__(self, train_path=['2020.train.json', '2021.train.json'], test_path=['2020.test.json', '2021.test.json'],
                       val_path=['2020.dev.json', '2021.dev.json'], dataset_name='Tweetner7', labels_path='label.json', dataset_dir=os.path.dirname(os.path.abspath(__file__))):
        super().__init__(train_path, test_path, val_path, dataset_name, labels_path, dataset_dir)

    def _map_original_labels_to_new_labels(self, tag, original_id_to_label_mapping):
        label = original_id_to_label_mapping[tag]
        new_id = label_to_id_mapping[label]
        return new_id

    def _clear_tokens(self, tokens):
        # remove {{, }}, {@, @} from tokens
        tokens = [token.replace("{{", "").replace("}}", "").replace("{@", "").replace("@}", "") for token in tokens]
        return tokens
        

    def _load(self, paths):
        ds = None
        for i in range(len(paths)):
            path = os.path.join(self.dataset_dir, paths[i])   
            data = []
            with open(path, 'r') as f:
                # read line by line
                lines = f.readlines()
                # each line is a json object
                for line in lines:
                    obj = json.loads(line)
                    data.append(obj)

            dataset = [
                {
                    "tokens": tf.convert_to_tensor(self._clear_tokens(obj['tokens']), dtype=tf.string),
                    "ner": tf.convert_to_tensor([self._map_original_labels_to_new_labels(label, tweetner_to_dataset_mapping) for label in obj['tags']], dtype=tf.int64),
                    "pos": 0,    # purely for compatibility with conll dataset
                    "chunks": 0, # purely for compatibility with conll dataset
                } for obj in data
            ]
            if ds is None:
                ds = tf.data.Dataset.from_generator(lambda: dataset, output_types={"tokens": tf.string, "ner": tf.int64, "pos": tf.int64, "chunks": tf.int64})
            else:
                ds = ds.concatenate(tf.data.Dataset.from_generator(lambda: dataset, output_types={"tokens": tf.string, "ner": tf.int64, "pos": tf.int64, "chunks": tf.int64}))
        return ds

    def load(self, split):
        if split == Split.TRAIN:
            return self._load(self.train_path)
        elif split == Split.TEST:
            return self._load(self.test_path)
        elif split == Split.VAL:
            return self._load(self.val_path)
        elif split == Split.TRAIN_RANDOM:
            return self._load(['random.train.json'])
        elif split == Split.VAL_RANDOM:
            return self._load(['random.dev.json'])
        else:
            raise ValueError("Invalid split: {}".format(split))


if __name__ == "__main__":
    loader = Tweetner7Loader()
    ds = loader.load(Split.TRAIN)
    for d in ds.take(1):
        print(d)