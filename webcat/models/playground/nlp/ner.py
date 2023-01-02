from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from transformers import pipeline

def predict_manually():
    tokenizer = AutoTokenizer.from_pretrained("tner/roberta-large-tweetner-2020-selflabel2021-concat")
    model = AutoModelForTokenClassification.from_pretrained("tner/roberta-large-tweetner-2020-selflabel2021-concat")

    text = "Hey @alexpilar, how you doing in Tweetoshi?"
    tokens = tokenizer(text, add_special_tokens=True, return_tensors="pt")

    with torch.no_grad():
        # logits = model(**tokens).logits
        res = model(**tokens)
    # predicted_token_class_ids = logits.argmax(-1)
    # predicted_tokens_classes = [model.config.id2label[t.item()] for t in predicted_token_class_ids[0]]
    # print(predicted_tokens_classes)

    print(res)

def predict_with_pipeline(text):
    tokenizer = AutoTokenizer.from_pretrained("tner/roberta-large-tweetner-2020-selflabel2021-concat", add_special_tokens=True, return_tensors="pt")
    pipe = pipeline(task='token-classification', model="tner/roberta-large-tweetner-2020-selflabel2021-concat", tokenizer=tokenizer)
    res = pipe(text)
    return res
    # print(res)
    

if __name__ == "__main__":
    predict_with_pipeline("Hey man!")
