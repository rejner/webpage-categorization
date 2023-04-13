from transformers import pipeline
from transformers.pipelines.pt_utils import KeyDataset
import torch

class DeBerta_v3_large_mnli():
    path = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"
    name = "DeBERTa v3 Large MNLI"
    size = "870 MB"
    description = "A model trained on MNLI dataset using Microsoft's DeBERTa v3 base architecture."
    default_hypothesis = "The text provides information about {}."

    def __init__(self, init_labels=None) -> None:
        self.labels = ["drugs", "hacking", "fraud", "counterfeit goods", "cybercrime", "cryptocurrency"] if init_labels is None else init_labels
        self.model = pipeline("zero-shot-classification",
                model="webcat/model_repository/MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli", framework="pt", device=0 if torch.cuda.is_available() else -1)
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
        results = self.model(dataset, labels, multi_label=True, hypothesis_template=hypothesis_template, batch_size=batch_size, truncation=True)
        return [dict(zip(result["labels"], result["scores"])) for result in results]
