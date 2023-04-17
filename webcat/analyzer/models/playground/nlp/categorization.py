from transformers import pipeline
from articles import crypto_article, firearms_article, drugs_article, other_article, crime_article, IT_article
from articles import examples

def run_multi_example_classification_task():
    classifier = pipeline("zero-shot-classification")
    for article in examples:
        res = classifier(article,
            candidate_labels=["firearms", "drugs", "cryptocurrency", "crime", "animals", "information technology"],
            multi_label=True
            )
        print(f"Text: {res['sequence']}\nLabels: {res['labels']}\nScores: {res['scores']}\n")


def run_single_example_classification_task():
    classifier = pipeline("zero-shot-classification")
    text = "Damn Daniel, I'm so high right now. The pod was top quality good maaaannn....."
    res = classifier(crypto_article,
        candidate_labels=["weapons", "drugs", "cryptocurrency", "crime", "animals", "spam", "fraud", "scam"],
        multi_label=False
        )
    print(res)


if __name__ == "__main__":
    # run_multi_example_classification_task()
    run_single_example_classification_task()