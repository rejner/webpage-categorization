from transformers import pipeline
from transformers.pipelines.pt_utils import KeyDataset
import torch
import logging

class BARTLarge():
    """
    A class representing a BART Large MNLI model.

    Attributes:
    - path (str): The path to the BART Large MNLI model.
    - name (str): The name of the BART Large MNLI model.
    - size (str): The size of the BART Large MNLI model.
    - description (str): A description of the BART Large MNLI model.
    - default_hypothesis (str): The default hypothesis for the BART Large MNLI model.

    Methods:
    - get_device(): Returns the device to use for the BART Large MNLI model.
    - __init__(self, init_labels=None): Initializes a BARTLarge object.
    - determine_params(self, **kwargs): Determines the parameters for the BART Large MNLI model.
    - classify(self, inputs, **kwargs): Classifies the inputs using the BART Large MNLI model.
    - classify_dataset(self, dataset, **kwargs): Classifies the dataset using the BART Large MNLI model.
    """
        
    path = "facebook/bart-large-mnli"
    name = "BART Large MNLI"
    size = "1.6 GB"
    description = "A model trained on MNLI dataset using BART Large."
    default_hypothesis = "The subject of this article is {}."

    def get_device(self):
        device = 0 if torch.cuda.is_available() else -1
        # test for apple silicon mps
        if device == -1 and torch.backends.mps.is_available():
            device = torch.device("mps")
        logging.info(f"(Torch) Using device {device}")
        return device

    def __init__(self, init_labels=None) -> None:
        self.labels = ["drugs", "hacking", "fraud", "counterfeit goods", "cybercrime", "cryptocurrency"] if init_labels is None else init_labels
        self.model = pipeline("zero-shot-classification",
                model="webcat/model_repository/facebook/bart-large-mnli", framework="pt", device=self.get_device())
        self.hypothesis_template = "Talks about {}."
        self.batch_size = 8

    def determine_params(self, **kwargs):
        labels = self.labels if "labels" not in kwargs else kwargs["labels"]
        hypothesis_template = self.hypothesis_template if "hypothesis_template" not in kwargs else kwargs["hypothesis_template"]
        batch_size = self.batch_size if "batch_size" not in kwargs else kwargs["batch_size"]
        return labels, hypothesis_template, batch_size

    def classify(self, inputs, **kwargs):
        labels, hypothesis_template, _ = self.determine_params(**kwargs)
        results = self.model(inputs, labels, multi_label=True, hypothesis_template=hypothesis_template)
        return [dict(zip(result["labels"], result["scores"])) for result in results]

    def classify_dataset(self, dataset, **kwargs):
        labels, hypothesis_template, batch_size = self.determine_params(**kwargs)
        dataset = KeyDataset(dataset, "text")
        results = self.model(dataset, labels, multi_label=True, hypothesis_template=hypothesis_template, batch_size=batch_size)
        return [dict(zip(result["labels"], result["scores"])) for result in results]
