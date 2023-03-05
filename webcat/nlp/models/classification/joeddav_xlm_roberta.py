from transformers import pipeline

class XLMRobertaLarge():
    def __init__(self, init_labels=None) -> None:
        self.labels = ["drugs", "hacking", "fraud", "counterfeit goods", "cybercrime", "cryptocurrency"] if init_labels is None else init_labels
        self.model = pipeline("zero-shot-classification",
                model="joeddav/xlm-roberta-large-xnli", framework="pt", device=0)
        self.hypothesis_template = "Talks about {}."

    def determine_params(self, **kwargs):
        labels = self.labels if "labels" not in kwargs else kwargs["labels"]
        hypothesis_template = self.hypothesis_template if "hypothesis_template" not in kwargs else kwargs["hypothesis_template"]
        return labels, hypothesis_template

    def classify(self, inputs, **kwargs):
        labels, hypothesis_template = self.determine_params(**kwargs)
        results = self.model(inputs, labels, multi_label=True, hypothesis_template=hypothesis_template)
        return [dict(zip(result["labels"], result["scores"])) for result in results]

