import abc

# define Split enum
class Split:
    TRAIN = 'train'
    TEST = 'test'
    VAL = 'dev'
    TRAIN_RANDOM = 'train_random'
    VAL_RANDOM = 'dev_random'

id_to_label_mapping = {0: "O", 1: "B-PER", 2: "I-PER", 3: "B-ORG", 
                       4:"I-ORG", 5: "B-LOC", 6: "I-LOC", 7: "B-MISC", 8: "I-MISC", 9: "B-PROD", 10: "I-PROD"
                       }
label_to_id_mapping = {v: k for k, v in id_to_label_mapping.items()}

class DatasetLoaderInterface(metaclass=abc.ABCMeta):
    def __init__(self, train_path, test_path, val_path, dataset_name, labels_path, dataset_dir):
        self.train_path = train_path
        self.test_path = test_path
        self.val_path = val_path
        self.dataset_name = dataset_name
        self.labels_path = labels_path
        self.dataset_dir = dataset_dir

    @abc.abstractmethod
    def load(self, split):
        pass