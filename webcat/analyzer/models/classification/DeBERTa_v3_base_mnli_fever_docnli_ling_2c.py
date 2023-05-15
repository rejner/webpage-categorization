from transformers import pipeline
from transformers.pipelines.pt_utils import KeyDataset
import torch
import logging

class DeBerta_v3_base_mnli_fever_docnli_ling_2c():
    """
    A class representing a DeBERTa v3 base model trained on MNLI, FEVER, DOCNLI, LING, 2C datasets.

    Attributes:
        path (str): The path to the model.
        name (str): The name of the model.
        size (str): The size of the model.
        description (str): A description of the model.
        default_hypothesis (str): The default hypothesis for zero-shot classification.
        labels (list): The list of labels for zero-shot classification.
        model (pipeline): The DeBERTa v3 base model pipeline.
        hypothesis_template (str): The hypothesis template for zero-shot classification.
        batch_size (int): The batch size for zero-shot classification.

    Methods:
        get_device(): Returns the device to use for the model.
        determine_params(**kwargs): Determines the parameters for zero-shot classification.
        classify(inputs, **kwargs): Classifies the inputs using zero-shot classification.
        classify_dataset(dataset, **kwargs): Classifies the dataset using zero-shot classification.
    """
        
    path = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-docnli-ling-2c"
    name = "DeBERTa v3 base MNLI FEVER DocNLI Ling 2c"
    size = "369 MB"
    description = "A model trained on MNLI datasets using Microsoft's DeBERTa v3 base architecture."
    default_hypothesis = "This text covers the topic of {}."

    def __init__(self, init_labels=None) -> None:
        self.labels = ["drugs", "hacking", "fraud", "counterfeit goods", "cybercrime", "cryptocurrency"] if init_labels is None else init_labels
        self.model = pipeline("zero-shot-classification",
                model="webcat/model_repository/MoritzLaurer/DeBERTa-v3-base-mnli-fever-docnli-ling-2c", framework="pt", device=self.get_device())
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
