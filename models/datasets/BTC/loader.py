import sys
import os
import tensorflow as tf
sys.path.append("/workspaces/webpage_categorization")

from models.datasets.loader_interace import DatasetLoaderInterface, Split, id_to_label_mapping, label_to_id_mapping
from models.datasets.utils.utils import read_NER_output

class BTCLoader(DatasetLoaderInterface):
    def __init__(self, train_path=None, test_path=None,
                       val_path=None, dataset_name='BTC', labels_path=None, dataset_dir=os.path.dirname(os.path.abspath(__file__))):
        super().__init__(train_path, test_path, val_path, dataset_name, labels_path, dataset_dir)
        self.dataset_chunks = [
            "a.conll",
            "b.conll",
            "e.conll",
            "f.conll",
            "g.conll",
            "h.conll",
        ]

    def _load(self, path):
        path = os.path.join(self.dataset_dir, path)
        ds = read_NER_output(path)
        dataset = [{
            "tokens": tf.convert_to_tensor([el[0][0] for el in sentance]),
            "ner": tf.convert_to_tensor([label_to_id_mapping[el[1]] for el in sentance], dtype=tf.int64)
        } for sentance in ds]
        ds = tf.data.Dataset.from_generator(lambda: dataset, output_types={"tokens": tf.string, "ner": tf.int64})
        return ds

    def load(self, split):
        if split == Split.TRAIN:
            return self._load(self.dataset_chunks[0])
        elif split == Split.TEST:
            return self._load(self.dataset_chunks[1])
        elif split == Split.VAL:
            return self._load(self.dataset_chunks[2])
        else:
            raise ValueError("Invalid split: {}".format(split))


if __name__ == "__main__":
    loader = BTCLoader()
    ds = loader.load(Split.TRAIN)
    for d in ds.take(1):
        print(d)