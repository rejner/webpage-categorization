from transformers import pipeline
from articles import crypto_article, firearms_article, drugs_article, other_article, crime_article

classifier = pipeline("zero-shot-classification")

res = classifier(firearms_article,
    candidate_labels=["firearms", "drugs", "crypto", "crime", "animals"],
    multi_label=True
    )

print(res)