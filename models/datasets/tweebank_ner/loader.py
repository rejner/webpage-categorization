import sys
import os
import json
import tensorflow as tf
sys.path.append("/workspaces/webpage_categorization")

from models.datasets.loader_interace import DatasetLoaderInterface, Split, id_to_label_mapping, label_to_id_mapping

class TweebankNERLoader(DatasetLoaderInterface):
    def __init__(self, train_path='./train.json', test_path='test.json',
                       val_path='valid.json', dataset_name='Tweebank', labels_path='label.json', dataset_dir=os.path.dirname(os.path.abspath(__file__))):
        super().__init__(train_path, test_path, val_path, dataset_name, labels_path, dataset_dir)

    def _map_original_labels_to_new_labels(self, tag, original_id_to_label_mapping):
        label = original_id_to_label_mapping[tag]
        new_id = label_to_id_mapping[label]
        return new_id

    def _load(self, path):
        path = os.path.join(self.dataset_dir, path)
        mapping_path = os.path.join(self.dataset_dir, self.labels_path)
        data = []
        with open(mapping_path, 'r') as f:
            original_label_to_id_mapping = json.load(f)        
            original_id_to_label_mapping = {v: k for k, v in original_label_to_id_mapping.items()}


        with open(path, 'r') as f:
            # read line by line
            lines = f.readlines()
            # each line is a json object
            for line in lines:
                obj = json.loads(line)
                data.append(obj)

        dataset = [
            {
                "tokens": tf.convert_to_tensor(obj['tokens'], dtype=tf.string),
                "ner": tf.convert_to_tensor([self._map_original_labels_to_new_labels(label, original_id_to_label_mapping) for label in obj['tags']], dtype=tf.int64),
                "pos": 0,    # purely for compatibility with conll dataset
                "chunks": 0, # purely for compatibility with conll dataset
            } for obj in data
        ]
        ds = tf.data.Dataset.from_generator(lambda: dataset, output_types={"tokens": tf.string, "ner": tf.int64, "pos": tf.int64, "chunks": tf.int64})
        return ds

    def load(self, split):
        if split == Split.TRAIN:
            return self._load(self.train_path)
        elif split == Split.TEST:
            return self._load(self.test_path)
        elif split == Split.VAL:
            return self._load(self.val_path)
        else:
            raise ValueError("Invalid split: {}".format(split))


if __name__ == "__main__":
    loader = TweebankNERLoader()
    ds = loader.load(Split.TRAIN)
    for d in ds.take(1):
        print(d)