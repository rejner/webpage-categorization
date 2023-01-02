from transformers import AutoTokenizer, AutoModelForTokenClassification

class TweetNER7():
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained("tner/twitter-roberta-base-dec2021-tweetner7-random")
        self.model = AutoModelForTokenClassification.from_pretrained("tner/twitter-roberta-base-dec2021-tweetner7-random")
        self.model.to("cuda")
        self.NER_MAPPING = {
            0: "B-corporation",
            1: "B-creative_work",
            2: "B-event",
            3: "B-group",
            4: "B-location",
            5: "B-person",
            6: "B-product",
            7: "I-corporation",
            8: "I-creative_work",
            9: "I-event",
            10: "I-group",
            11: "I-location",
            12: "I-person",
            13: "I-product",
            14: "O"
        }

    def classify(self, inputs):
        x = self.tokenizer(inputs, return_tensors="pt", padding=True).to("cuda")
        y = self.model(**x)
        logits = y.logits.to("cpu")
        res = [logits[i].argmax(axis=-1).numpy() for i in range(len(inputs))]
        res = [[self.NER_MAPPING[i] for i in res[i]] for i in range(len(inputs))]
        
        texts = [self.tokenizer.convert_ids_to_tokens(x["input_ids"][i]) for i in range(len(inputs))]

        for i in range(len(res)):
            for j in range(len(res[i])):
                if res[i][j].startswith("B-") or res[i][j].startswith("I-"):
                    entity = res[i][j].split("-")[1]
                    if entity not in ['product', 'person']:
                        continue
                    texts[i][j] = "<{}>".format(res[i][j].split("-")[1]) + texts[i][j] + "</{}>".format(res[i][j].split("-")[1])

        # transfer t1 back to text
        texts = [self.tokenizer.convert_tokens_to_string(texts[i]) for i in range(len(texts))]
        # remove Ġ symbols
        texts = [texts[i].replace("Ġ", "") for i in range(len(texts))]
        # replace all <pad> with empty string
        texts = [texts[i].replace("<pad>", "") for i in range(len(texts))]

        return res, texts
