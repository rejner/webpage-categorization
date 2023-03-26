from transformers import AutoTokenizer, AutoModelForTokenClassification
import logging

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

    def get_entity_types(self):
        # return list of entity types without O and prefix B- and I-
        return set([self.NER_MAPPING[i].split("-")[1] for i in range(len(self.NER_MAPPING)) if i != 14])
        
    def annotate_text(self, texts, res):
        for i in range(len(res)):
            for j in range(len(res[i])):
                if res[i][j].startswith("B-") or res[i][j].startswith("I-"):
                    entity = res[i][j].split("-")[1]
                    if entity not in ['product', 'person']:
                        continue
                    if res[i][j].startswith("B-"):
                        texts[i][j] = " <{}>".format(res[i][j].split("-")[1]) + texts[i][j] + "</{}>".format(res[i][j].split("-")[1])
                    else:
                        texts[i][j] = "<{}>".format(res[i][j].split("-")[1]) + texts[i][j] + "</{}>".format(res[i][j].split("-")[1])
        return texts


    def clear_text_outputs(self, texts):
        # transfer t1 back to text
        texts = [self.tokenizer.convert_tokens_to_string(texts[i]) for i in range(len(texts))]
        texts = [texts[i].replace("<s>", "") for i in range(len(texts))]
        texts = [texts[i].replace("</s>", "") for i in range(len(texts))]
        # remove Ġ symbols
        texts = [texts[i].replace("Ġ", "") for i in range(len(texts))]
        # replace all <pad> with empty string
        texts = [texts[i].replace("<pad>", "") for i in range(len(texts))]
        return texts

    def extract_whole_entities(self, texts, res):
        """
        Extract whole entities from texts and res.
        Start of entity is marked with B- and any following tokens are marked with I-.
        Also store the entity type.
        """
        entities = []
        for i in range(len(res)):
            entities.append([])
            entity = ""
            for j in range(len(res[i])):
                if res[i][j].startswith("B-"):
                    entity = texts[i][j]
                elif res[i][j].startswith("I-"):
                    entity += texts[i][j]
                elif entity != "":
                    entity = entity.replace("Ġ", "")
                    entities[i].append((entity, res[i][j-1].split("-")[1]))
                    entity = ""

        return entities


    def classify(self, inputs):
        x = self.tokenizer(inputs, return_tensors="pt", padding=True).to("cuda")
        y = self.model(**x)
        logits = y.logits.to("cpu")
        res = [logits[i].argmax(axis=-1).numpy() for i in range(len(inputs))]
        res = [[self.NER_MAPPING[i] for i in res[i]] for i in range(len(inputs))]
        
        texts = [self.tokenizer.convert_ids_to_tokens(x["input_ids"][i]) for i in range(len(inputs))]
        entities = self.extract_whole_entities(texts, res)
        # texts = self.annotate_text(texts, res)
        texts = self.clear_text_outputs(texts)
        

        return entities, texts
