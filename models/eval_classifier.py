import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from transformers import pipeline
import json
import datasets
from transformers.pipelines.pt_utils import KeyDataset
import time
import tqdm

model_dir = "webcat/model_repository"

from webcat.nlp.models import list_all_models


def load_dataset(path):
    """
        Load a dataset from a file.
    """
    # with open(path, "r") as f:
    #     data = json.load(f)
    dataset = datasets.Dataset.from_json(path)
    return dataset


# create a new column from headline and short_description
def concat_text(example):
    example['text'] = f"{example['headline']}. {example['short_description']}"
    return example


def find_best_hypothesis_template(dataset, models, categories):
    hypothesis_template = "The topic of this article is {}." # 0.28
    hypothesis_template = "This article is about {}." # 0.39
    hypothesis_template = "This example is about {}." # 0.57
    hypothesis_template = "This text is about {}." # 0.49
    hypothesis_template = "The main subject of this text is {}." # 0.25
    hypothesis_template = "The focus of this writing is on {}." # 0.26
    hypothesis_template = "The primary topic of discussion in this text is {}." # 0.17
    hypothesis_template = "This article discusses {}." # 0.62
    hypothesis_template = "The main idea presented in this text is {}." # 0.26
    hypothesis_template = "The primary subject matter of this article is {}." # 0.19
    hypothesis_template = "The subject of this article is {}." # 0.28
    hypothesis_template = "This text covers the topic of {}." # 0.66
    hypothesis_template = "This article examines {}." # 0.56
    hypothesis_template = "The main focus of this text is {}." # 0.22
    hypothesis_template = "This article presents information on {}." # 0.57
    hypothesis_template = "The main topic covered in this text is {}." # 0.24
    hypothesis_template = "The central theme of this article is {}." # 0.21
    hypothesis_template = "This text provides insights into {}." # 0.52
    hypothesis_template = "The primary objective of this article is to discuss {}." # 0.12
    hypothesis_template = "This text examines the topic of {} in depth." # 0.27
    hypothesis_template = "The topic of this text is {}." # 0.32
    hypothesis_template = "This article delves into the topic of {}." # 0.54

    # put all templates into list
    hypothesis_templates = ["The topic of this article is {}.", "This article is about {}.", "This example is about {}.", "This text is about {}.", "The main subject of this text is {}.", "The focus of this writing is on {}.", "The primary topic of discussion in this text is {}.", "This article discusses {}.", "The main idea presented in this text is {}.", "The primary subject matter of this article is {}.", "The subject of this article is {}.", "This text covers the topic of {}.", "This article examines {}.", "The main focus of this text is {}.", "This article presents information on {}.", "The main topic covered in this text is {}.", "The central theme of this article is {}.", "This text provides insights into {}.", "This text examines the topic of {} in depth.", "The topic of this text is {}.", "This article delves into the topic of {}."]
    # hypothesis_templates = [
    #     "The main focus of this text on {}.", "This example is about {}.", "This example is mainly about {}."
    # ]
    # hypothesis_templates = [
    #     "This text examines the topic of {} in depth.", "The subject of this article is {}.", "This text covers the topic of {}.", "This example is about {}."
    # ]

    template_stats = {}

    for model in models:
        if model['task'] != 'classification':
            continue

        print(f"Model: {model['model']}")
        template_stats[model['model']] = {}
        # if model['model'] != "facebook/bart-large-mnli":
        # if model['model'] != "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli" or model['model'] != "MoritzLaurer/DeBERTa-v3-base-mnli":
        #     continue


        tokenizer = model["tokenizer_class"].from_pretrained(model_dir + "/" + model['model'])
        mod = model["model_class"].from_pretrained(model_dir + "/" + model['model'])
        pipe = pipeline(model["pipeline"], model=mod, tokenizer=tokenizer, device=0, framework="pt")

        for hypothesis_template in hypothesis_templates:

            predictions = []
            for result in tqdm.tqdm(pipe(KeyDataset(dataset, "text"), categories, multi_label=True, hypothesis_template=hypothesis_template, batch_size=32, truncation=True), total=len(dataset)):
                predictions.append([label.upper() for label, score in zip(result["labels"], result["scores"]) if score > 0.8])

            # if prediction column already exists, remove it
            if "prediction" in dataset.column_names:
                dataset = dataset.remove_columns("prediction")
            dataset = dataset.add_column("prediction", predictions)

            # calculate accuracy
            precisions = []
            recalls = []
            for i in range(len(dataset)):
                precision, recall = evaluate_sample(dataset[i]['prediction'], dataset[i]['category'])
                precisions.append(precision)
                recalls.append(recall)
            
            if len(precisions) == 0 or len(recalls) == 0:
                print("wtf")

            print("----------------------------------")
            print(f"Template: {hypothesis_template}")
            print(f"Precision: {sum(precisions) / len(precisions)}")
            print(f"Recall: {sum(recalls) / len(recalls)}")
            print(f"F1: {2 * (sum(precisions) / len(precisions)) * (sum(recalls) / len(recalls)) / ((sum(precisions) / len(precisions)) + (sum(recalls) / len(recalls)))}")
            print("----------------------------------")

            template_stats[model['model']][hypothesis_template] = {
                "precision": sum(precisions) / len(precisions),
                "recall": sum(recalls) / len(recalls),
                "f1": 2 * (sum(precisions) / len(precisions)) * (sum(recalls) / len(recalls)) / ((sum(precisions) / len(precisions)) + (sum(recalls) / len(recalls)))
            }

        # print(f"Best template: {max(template_stats, key=lambda key: template_stats[key]['f1'])}")

    # pretty print dict
    print(json.dumps(template_stats, indent=5))


def evaluate_sample(predictions, true_labels):
    num_predictions = len(predictions)
    if isinstance(true_labels, str):
        true_labels = [true_labels]
    num_true_labels = len(true_labels)
    true_positives = 0
    false_positives = 0
    
    for category in predictions:
        if category in true_labels:
            true_positives += 1
        else:
            false_positives += 1
    
    precision = 0
    recall = 0
    if num_predictions > 0:
        precision = true_positives / num_predictions

    if num_true_labels > 0:
        recall = true_positives / num_true_labels
    
    # Penalize for additional categories
    penalty_factor = 0
    if num_predictions > num_true_labels:
        penalty_factor = 1 - (1 / num_predictions)
        
    modified_precision = precision - (penalty_factor * precision)
    
    return (modified_precision, recall)

if __name__ == "__main__":
    """
        Load all models and run a test on them.
    """
    models = list_all_models()
    dataset = load_dataset("data/categorization/News_Category_Dataset_v3.json")

    discarded_categories = ['U.S. NEWS', 'THE WORLDPOST', 'WORLD NEWS', 'WEIRD NEWS', 'GOOD NEWS', 'WORLDPOST', 'IMPACT']
    # remove all 'U.S. NEWS' category examples
    dataset = dataset.filter(lambda x: x['category'] not in discarded_categories)

    categories = [cat for cat in list(set(dataset['category'])) if cat not in discarded_categories]
    categories = [cat.lower() for cat in categories]

    hypothesis_template = "This text provides insights into {}."

    print(dataset.column_names)
    print(categories)
    # show some examples
    # for i in range(10):
    #     print(dataset[i])
        
    # take only 200 examples
    dataset = dataset.select(range(1000)).shuffle()

    # create a new column from headline and short_description (map function)
    dataset = dataset.map(concat_text, batched=False)

    find_best_hypothesis_template(dataset, models, categories)
    
    exit(0)

    for model in models:
        if model['task'] != 'classification':
            continue

        print(f"Model: {model['model']}")
        if model['model'] != "facebook/bart-large-mnli":
            continue


        tokenizer = model["tokenizer_class"].from_pretrained(model_dir + "/" + model['model'])
        mod = model["model_class"].from_pretrained(model_dir + "/" + model['model'])
        pipe = pipeline(model["pipeline"], model=mod, tokenizer=tokenizer, device=0, framework="pt")



        predictions = []
        for result in tqdm.tqdm(pipe(KeyDataset(dataset, "text"), categories, multi_label=True, hypothesis_template=hypothesis_template, batch_size=32, truncation=True), total=len(dataset)):
            predictions.append([label.upper() for label, score in zip(result["labels"], result["scores"]) if score > 0.8])

        # if prediction column already exists, remove it
        if "prediction" in dataset.column_names:
            dataset = dataset.remove_columns("prediction")
        dataset = dataset.add_column("prediction", predictions)

        # calculate accuracy
        precisions = []
        recalls = []
        for i in range(len(dataset)):
            precision, recall = evaluate_sample(dataset[i]['prediction'], dataset[i]['category'])
            precisions.append(precision)
            recalls.append(recall)
        
        print(f"Precision: {sum(precisions) / len(precisions)}")
        print(f"Recall: {sum(recalls) / len(recalls)}")
        print(f"F1: {2 * (sum(precisions) / len(precisions)) * (sum(recalls) / len(recalls)) / ((sum(precisions) / len(precisions)) + (sum(recalls) / len(recalls)))}")

        
        for i in range(30):
            print("-"*60)
            print(dataset[i]['category'])
            print(dataset[i]['prediction'])
            print(dataset[i]['text'])
            print("-"*60)

        
        


    