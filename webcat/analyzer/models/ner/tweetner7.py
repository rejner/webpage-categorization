from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline, Pipeline
from transformers.pipelines.pt_utils import KeyDataset
import torch
from transformers.pipelines import PIPELINE_REGISTRY

class TweetNER7():
    path = "tner/twitter-roberta-base-dec2021-tweetner7-random"
    name = "RoBERTa base TweetNER7"
    size = "484 MB"
    description = "A model trained on the TweetNER7 dataset using the RoBERTa base architecture."

    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained("webcat/model_repository/tner/twitter-roberta-base-dec2021-tweetner7-random")
        self.model = AutoModelForTokenClassification.from_pretrained("webcat/model_repository/tner/twitter-roberta-base-dec2021-tweetner7-random")
        self.model.to("cuda" if torch.cuda.is_available() else "cpu")
        self.model.eval()

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

    def print_entity_text_side_by_side(self, texts, res):
        # each text is a list of tokens, print them vertically with the corresponding entity
        for i in range(len(res)):
            print("Text {}: ".format(i))
            # print text and entity side by side aligned
            for j in range(len(res[i])):
                print("{:20} {:20}".format(texts[i][j], res[i][j]))
            print("")

    def extract_whole_entities(self, texts, res):
        """
        Extract whole entities from texts and res.
        Start of entity is marked with B- and any following tokens are marked with I-.
        Also store the entity type.
        """
        def clear_entity(entity):
            entity = entity.replace("Ġ", " ")
            # remove leading and trailing whitespaces or special characters
            entity = entity.strip(" ,.!?;:()[]{}")
            return entity
        
        # print("Extracting whole entities...")
        # self.print_entity_text_side_by_side(texts, res)
        entities = []
        for i in range(len(res)):
            entities.append([])
            entity = ""
            entity_type = ""
            entity_stack = []
            for j in range(len(res[i])):
                if res[i][j].startswith("B-"):
                    if entity != "":
                        entity = clear_entity(entity)
                        entities[i].append((entity, entity_type))
                    entity_stack.append((entity, entity_type))
                    entity = texts[i][j]
                    entity_type = res[i][j].split("-")[1]
                elif res[i][j].startswith("I-"):
                    entity += texts[i][j]
                elif res[i][j].startswith("O"):
                    if entity != "":
                        entity = clear_entity(entity)
                        entities[i].append((entity, entity_type))
                        entity = ""
                        entity_type = ""
                    if entity_stack:
                        entity, entity_type = entity_stack.pop()
            # If there's still an entity left
            if entity != "":
                entity = clear_entity(entity)
                entities[i].append((entity, entity_type))
                entity = ""
                entity_type = ""

        # Remove empty entities
        for i in range(len(entities)):
            entities[i] = list(set(entities[i]))
            for entity in entities[i]:
                if entity[0] == "" or entity[1] == "":
                    entities[i].remove(entity)

        # print("Extracted entities: ", entities)
        return entities

    def classify(self, inputs):
        x = self.tokenizer(inputs, return_tensors="pt", padding=True)
        if torch.cuda.is_available():
            x = x.to("cuda")
        y = self.model(**x)
        logits = y.logits.to("cpu")
        res = [logits[i].argmax(axis=-1).numpy() for i in range(len(inputs))]
        res = [[self.NER_MAPPING[i] for i in res[i]] for i in range(len(inputs))]
        
        texts = [self.tokenizer.convert_ids_to_tokens(x["input_ids"][i]) for i in range(len(inputs))]
        entities = self.extract_whole_entities(texts, res)
        # texts = self.annotate_text(texts, res)
        texts = self.clear_text_outputs(texts)
        return entities, texts
    
    def classify_dataset(self, dataset):
        dataset = KeyDataset(dataset, "text")
        pipe = pipeline("webcat-ner", model=self.model, tokenizer=self.tokenizer, device=0 if torch.cuda.is_available() else -1)
        res = pipe(dataset, batch_size=1)
        entities = []
        texts = []

        # iterate over res, sometime error can occur, but just ignore it and continue
        try:
            for out in res:
                try:
                    entities.append(out["entities"])
                    texts.append(out["texts"])
                except Exception as e:
                    print(e)
                    continue

        except Exception as e:
            print(e)
            pass
        # flatten the list
        entities = [item for sublist in entities for item in sublist]
        texts = [item for sublist in texts for item in sublist]
        return entities, texts
    
        
class WebCatNERPipeline(Pipeline):
    def __init__(self, model, tokenizer, framework="pt", **kwargs):
        super().__init__(model=model, tokenizer=tokenizer, framework=framework, **kwargs)
        self.model = model
        self.tokenizer = tokenizer
        self.framework = framework
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
    def _sanitize_parameters(self, **kwargs):
        preprocess_kwargs = {}
        return preprocess_kwargs, {}, {}

    def preprocess(self, inputs):
        return self.tokenizer(inputs, return_tensors=self.framework, padding=True)

    def _forward(self, model_inputs):
        model_outputs = self.model(**model_inputs)
        return {"logits": model_outputs.logits, "input_ids": model_inputs["input_ids"]}

    def postprocess(self, model_outputs):
        model_inputs = model_outputs["input_ids"]
        outputs = model_outputs['logits'].argmax(axis=-1).cpu().numpy()
        outputs = [[self.NER_MAPPING[token] for token in output] for output in outputs]
        texts = [self.tokenizer.convert_ids_to_tokens(input) for input in model_inputs]
        entities = self.extract_whole_entities(texts, outputs)
        texts = self.clear_text_outputs(texts)
        return {"entities": entities, "texts": texts}

    def extract_whole_entities(self, texts, res):
        """
        Extract whole entities from texts and res.
        Start of entity is marked with B- and any following tokens are marked with I-.
        Also store the entity type.
        """
        def clear_entity(entity):
            entity = entity.replace("Ġ", " ")
            # remove leading and trailing whitespaces or special characters
            entity = entity.strip(" ,.!?;:()[]{}")
            return entity
        
        # print("Extracting whole entities...")
        # self.print_entity_text_side_by_side(texts, res)
        entities = []
        for i in range(len(res)):
            entities.append([])
            entity = ""
            entity_type = ""
            entity_stack = []
            for j in range(len(res[i])):
                if res[i][j].startswith("B-"):
                    if entity != "":
                        entity = clear_entity(entity)
                        entities[i].append((entity, entity_type))
                    entity_stack.append((entity, entity_type))
                    entity = texts[i][j]
                    entity_type = res[i][j].split("-")[1]
                elif res[i][j].startswith("I-"):
                    entity += texts[i][j]
                elif res[i][j].startswith("O"):
                    if entity != "":
                        entity = clear_entity(entity)
                        entities[i].append((entity, entity_type))
                        entity = ""
                        entity_type = ""
                    if entity_stack:
                        entity, entity_type = entity_stack.pop()
            # If there's still an entity left
            if entity != "":
                entity = clear_entity(entity)
                entities[i].append((entity, entity_type))
                entity = ""
                entity_type = ""

        # Remove empty entities
        for i in range(len(entities)):
            entities[i] = list(set(entities[i]))
            for entity in entities[i]:
                if entity[0] == "" or entity[1] == "":
                    entities[i].remove(entity)

        # print("Extracted entities: ", entities)
        return entities
    
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
    
PIPELINE_REGISTRY.register_pipeline(
    "webcat-ner",
    pipeline_class=WebCatNERPipeline,
    pt_model=AutoModelForTokenClassification,
)

import timeit
def test_pipeline_speed(corpus):
    tokenizer = AutoTokenizer.from_pretrained("tner/twitter-roberta-base-dec2021-tweetner7-random")
    model = AutoModelForTokenClassification.from_pretrained("tner/twitter-roberta-base-dec2021-tweetner7-random")
    import datasets

    def inference(model, tokenizer, dataset):
        pipe = pipeline("webcat-ner", model=model, tokenizer=tokenizer, device=0)
        res = pipe(dataset, batch_size=32, num_workers=8)
        entities = []
        texts = []
        for out in res:
            entities.append(out["entities"])
            texts.append(out["texts"])
        
        # flatten entities
        entities = [item for sublist in entities for item in sublist]
        print(len(entities))
        print(entities[:10])
        return res
    

    dataset = datasets.Dataset.from_list([{ "text": item } for item in corpus])
    dataset = KeyDataset(dataset, "text")
    # dataset = datasets.load_dataset("superb", name="asr", split="test")
    # for item in dataset:
    #     print(item)
    #     break
    print("Starting pipeline inference...")
    time_taken = timeit.timeit(lambda: inference(model, tokenizer, dataset), number=1)
    print("Time taken [pipeline]: ", time_taken)
    

    

def test_classic_speed(corpus):
    ner_model = TweetNER7()

    def inference(model, corpus):
        corpus_iter = iter(corpus)
        batch = [next(corpus_iter) for _ in range(32)]
        entities = []
        # iterate over dataset
        while batch:
            res = model.classify(batch)
            entities.append(res)
            try:
                batch = [next(corpus_iter) for _ in range(32)]
            except StopIteration:
                break
        print(len(entities))

    print("Starting classic inference...")
    time_taken = timeit.timeit(lambda: inference(ner_model, corpus), number=1)
    print("Time taken [classic]: ", time_taken)


if __name__ == "__main__":
    from corpus import dummy_corpus
    # duplicate corpus 10 times
    corpus = dummy_corpus * 100
    print("Corpus length: ", len(corpus))
    test_pipeline_speed(corpus)
    test_classic_speed(corpus)