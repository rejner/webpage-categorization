from transformers import pipeline

class XLMRobertaLarge():
    def __init__(self, labels) -> None:
        self.labels = labels
        self.model = pipeline("zero-shot-classification",
                model="joeddav/xlm-roberta-large-xnli", framework="pt", device=0)
        self.hypothesis_template = "Talks about {}."

    def classify(self, inputs):
        results = self.model(inputs, self.labels, multi_label=True, hypothesis_template=self.hypothesis_template)
        return [dict(zip(result["labels"], result["scores"])) for result in results]

