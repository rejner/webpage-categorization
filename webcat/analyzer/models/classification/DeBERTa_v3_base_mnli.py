from transformers import pipeline
from transformers.pipelines.pt_utils import KeyDataset
import torch
import logging

class DeBerta_v3_base_mnli():
    """
    A class that wraps the DeBERTa v3 base architecture trained on the MNLI dataset for zero-shot classification
    of text inputs.

    Attributes:
        path (str): The path to the DeBERTa v3 base MNLI model.
        name (str): The name of the DeBERTa v3 base MNLI model.
        size (str): The size of the DeBERTa v3 base MNLI model.
        description (str): A description of the DeBERTa v3 base MNLI model.
        default_hypothesis (str): The default hypothesis template for zero-shot classification.

    Methods:
        __init__(self, init_labels=None): Initializes a DeBerta_v3_base_mnli object.
        get_device(self): Returns the device to use for running the model.
        determine_params(self, **kwargs): Determines the parameters to use for classification.
        classify(self, inputs, **kwargs): Classifies a list of text inputs.
        classify_dataset(self, dataset, **kwargs): Classifies a dataset of text inputs.

    """
        
    path = "MoritzLaurer/DeBERTa-v3-base-mnli"
    name = "DeBERTa v3 base MNLI"
    size = "720 MB"
    description = "A model trained on MNLI dataset using Microsoft's DeBERTa v3 base architecture."
    default_hypothesis = "This text covers the topic of {}."

    def __init__(self, init_labels=None) -> None:
        self.labels = ["drugs", "hacking", "fraud", "counterfeit goods", "cybercrime", "cryptocurrency"] if init_labels is None else init_labels
        self.model = pipeline("zero-shot-classification",
                model="webcat/model_repository/MoritzLaurer/DeBERTa-v3-base-mnli", framework="pt", device=self.get_device())
        self.hypothesis_template = "Talks about {}."
        self.batch_size = 8

    def get_device(self):
        device = 0 if torch.cuda.is_available() else -1
        # test for apple silicon mps
        if device == -1 and torch.backends.mps.is_available():
            device = torch.device("mps")
        logging.info(f"(Torch) Using device {device}")
        return device

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
        results = self.model(dataset, labels, multi_label=True, hypothesis_template=hypothesis_template, batch_size=batch_size, truncation=True)
        return [dict(zip(result["labels"], result["scores"])) for result in results]
