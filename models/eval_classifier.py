import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from transformers import pipeline
import json
import datasets
from transformers.pipelines.pt_utils import KeyDataset
import time
import tqdm
import pandas as pd
from sklearn import metrics
from matplotlib import pyplot as plt
import seaborn as sns
from collections import defaultdict
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
import pyarrow as pa
import re
import nltk
import urlextract
import datefinder

nltk.download('punkt')

url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
email_pattern = r'[\w\.-]+@[\w\.-]+'
datetime_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
html_pattern = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')





model_dir = "webcat/model_repository"

from webcat.nlp.processing.analyzer.models import list_all_models


def load_dataset(path):
    """
        Load a dataset from a file.
    """
    # with open(path, "r") as f:
    #     data = json.load(f)
    dataset = datasets.Dataset.from_json(path)
    return dataset


# create a new column from headline and short_description


def clear_text(text:str, remove_urls=True, remove_emails=True, remove_html_tags=True, remove_datetime=True):
    text = text.replace("\n", " ")
    # Remove all the tabs
    text = text.replace("\t", " ")
    # Remove all the multiple spaces
    text = re.sub(" +", " ", text)
    # Remove all the leading and trailing spaces

    text = text.strip()
    if text == "":
        return ""
    
    if remove_html_tags:
        text = html_pattern.sub(' ', text)
    
    # remove urls
    # urls = re.findall(url_pattern, text)
    try:
        if remove_urls:
            urls = urlextract.URLExtract().find_urls(text)
            for url in urls:
                text = text.replace(url, " [URL] ")
        # remove emails
        # emails = re.findall(email_pattern, text)
        if remove_emails:
            text = re.sub(email_pattern, " [EMAIL] ", text)

        # remove datetime
        if remove_datetime:
            matches = datefinder.find_dates(text, source=True, strict=True)
            for match, match_text in matches:
                text = text.replace(str(match_text), " [DATETIME] ")
    except Exception as e:
        return ""
        

    return text




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
    
    return precision, recall

def eval_model(model, dataset, categories, hypothesis_template, tag="0"):
    tokenizer = model["tokenizer_class"].from_pretrained(model_dir + "/" + model['model'])
    mod = model["model_class"].from_pretrained(model_dir + "/" + model['model'])
    pipe = pipeline(model["pipeline"], model=mod, tokenizer=tokenizer, device=0, framework="pt")

    # print(
    #     """
    #         Evaluating model:
    #         -----------------
    #         Model: {}
    #         Task: {}
    #         -----------------
    #     """.format(model['base_class'].name, model['task'])
    # )

    predictions = []
    for result in tqdm.tqdm(pipe(KeyDataset(dataset, "text"), categories, multi_label=True, hypothesis_template=hypothesis_template, batch_size=2, truncation=True), total=len(dataset)):
        predictions.append([label for label, score in zip(result["labels"], result["scores"]) if score > 0.8])

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
    
    precision = sum(precisions) / len(precisions)
    recall = sum(recalls) / len(recalls)
    f1 = 2 * precision * recall / (precision + recall)
    # print(f"F1: {f1}")
    # print(f"Precision: {precision}")
    # print(f"Recall: {recall}")
    print("f1: {}, precision: {}, recall: {}".format(f1, precision, recall))




    # prediction can be a list of categories
    # true label can be a list of categories

    # calculate confusion matrix
    confusion_matrix = {}
    # initialize confusion matrix
    for pred_category in categories:
        confusion_matrix[pred_category] = {}
        for gt_category in categories:
            confusion_matrix[pred_category][gt_category] = 0
    for i in range(len(dataset)):
        for prediction in dataset[i]['prediction']:
            # there is a one category in the true label
            if isinstance(dataset[i]['category'], str):
                confusion_matrix[prediction][dataset[i]['category']] += 1
            # there are multiple categories in the true label
            else:
                for category in dataset[i]['category']:
                    confusion_matrix[prediction][category] += 1


    # plot
    df_cm = pd.DataFrame(confusion_matrix, index = [i for i in categories],
                    columns = [i for i in categories])
    # large figure
    plt.figure( figsize=(20,20) )

    sns.heatmap(df_cm, annot=True, fmt='g')

    # save image
    plt.savefig(f"./confusion_matrix_{model['base_class'].name}_{tag}.png")


def load_news_category_dataset_v3(num_samples=100):
    def concat_text(example):
        example['text'] = f"{example['headline']}. {example['short_description']}"
        return example

    dataset = load_dataset("data/categorization/News_Category_Dataset_v3.json")

    discarded_categories = ['U.S. NEWS', 'THE WORLDPOST', 'WORLD NEWS', 'WEIRD NEWS', 'GOOD NEWS', 'WORLDPOST', 'IMPACT']
    # remove all 'U.S. NEWS' category examples
    dataset = dataset.filter(lambda x: x['category'] not in discarded_categories)

    categories = [cat for cat in list(set(dataset['category'])) if cat not in discarded_categories]
    categories = [cat.lower() for cat in categories]

    dataset = dataset.select(range(num_samples)).shuffle()
    dataset = dataset.map(concat_text, batched=False)

    return dataset, categories

def load_reuters_21578_dataset(num_samples=100):
    def concat_text_reuters(example):
        example['text'] = f"{example['title']}. {example['text']}"
        return example
    
    dataset = datasets.load_dataset("reuters21578", "ModApte")
    dataset = dataset['test']
    dataset = dataset.select(range(num_samples)).shuffle()

    # extract all categories by expanding the list of categories
    categories = []
    for i in range(len(dataset)):
        categories.extend(dataset[i]['topics'])
    categories = list(set(categories))
    categories = [cat.lower() for cat in categories]

    # remove all empty text examples
    dataset = dataset.filter(lambda x: x['text'] != "")

    # renamed topics to category
    dataset = dataset.rename_column("topics", "category")
    

    # create a new column from headline and short_description (map function)
    # dataset = dataset.map(concat_text_reuters, batched=False)

    return dataset, categories

def load_newsgroup_dataset(num_sample=100):
    if os.path.exists("models/newsgroup_dataset"):
        dataset = datasets.load_from_disk("models/newsgroup_dataset")

    category_splits = ['18828_alt.atheism', '18828_comp.graphics', '18828_comp.os.ms-windows.misc', '18828_comp.sys.ibm.pc.hardware', '18828_comp.sys.mac.hardware', '18828_comp.windows.x', '18828_misc.forsale', '18828_rec.autos', '18828_rec.motorcycles', '18828_rec.sport.baseball', '18828_rec.sport.hockey', '18828_sci.crypt', '18828_sci.electronics', '18828_sci.med', '18828_sci.space', '18828_soc.religion.christian', '18828_talk.politics.guns', '18828_talk.politics.mideast', '18828_talk.politics.misc', '18828_talk.religion.misc', '19997_alt.atheism', '19997_comp.graphics', '19997_comp.os.ms-windows.misc', '19997_comp.sys.ibm.pc.hardware', '19997_comp.sys.mac.hardware', '19997_comp.windows.x', '19997_misc.forsale', '19997_rec.autos', '19997_rec.motorcycles', '19997_rec.sport.baseball', '19997_rec.sport.hockey', '19997_sci.crypt', '19997_sci.electronics', '19997_sci.med', '19997_sci.space', '19997_soc.religion.christian', '19997_talk.politics.guns', '19997_talk.politics.mideast', '19997_talk.politics.misc', '19997_talk.religion.misc', 'bydate_alt.atheism', 'bydate_comp.graphics', 'bydate_comp.os.ms-windows.misc', 'bydate_comp.sys.ibm.pc.hardware', 'bydate_comp.sys.mac.hardware', 'bydate_comp.windows.x', 'bydate_misc.forsale', 'bydate_rec.autos', 'bydate_rec.motorcycles', 'bydate_rec.sport.baseball', 'bydate_rec.sport.hockey', 'bydate_sci.crypt', 'bydate_sci.electronics', 'bydate_sci.med', 'bydate_sci.space', 'bydate_soc.religion.christian', 'bydate_talk.politics.guns', 'bydate_talk.politics.mideast', 'bydate_talk.politics.misc', 'bydate_talk.religion.misc']
    shorts_to_long = {
        'alt': 'alternative',
        'comp': 'computer',
        'misc': 'miscellaneous',
        'pc': 'personal computer',
        'rec': 'recreational',
        'sci': 'science',
        'soc': 'social',
        'crypt': 'cryptography',
        'os': 'operating system',
        'med': 'medicine',
        'sys': 'system',
        'autos': 'cars',
    }
    discarded_categories = ['talk', 'social', 'x', 'mac', 'windows', 'ibm', 'mideast', 'alternative', 'miscellaneous', 'atheism',
                            'recreational', 'baseball', 'hockey', 'space', 'electronics', 'christian', 'operating system',
                            'personal computer', 'cryptography', 'system', 'graphics', 'ms-windows', 'science', 'hardware']

    if not os.path.exists("models/newsgroup_dataset"):
        dataset = datasets.Dataset(arrow_table=pa.Table.from_batches([], schema=pa.schema({'text': pa.string(), 'category': pa.list_(pa.string())})))
        for category_split in category_splits:
            dataset_part = datasets.load_dataset("newsgroup", category_split, split="train")
            dataset_part = dataset_part.map(lambda x: {'text': x['text'], 'category': category_split.split('_')[1].split('.')}, batched=False)
            # shorts_to_long on categories in 'category' column
            dataset_part = dataset_part.map(lambda x: {'text': x['text'], 'category': [shorts_to_long[cat] if cat in shorts_to_long else cat for cat in x['category']]}, batched=False)
            # remove all categories from 'category' column that are in discarded_categories
            dataset_part = dataset_part.map(lambda x: {'text': x['text'], 'category': [cat for cat in x['category'] if cat not in discarded_categories]}, batched=False)
            # remove all examples with empty category list
            dataset_part = dataset_part.filter(lambda x: len(x['category']) > 0)
            
            # add to dataset
            dataset = datasets.concatenate_datasets([dataset, dataset_part])
        
        dataset.save_to_disk("models/newsgroup_dataset")

    dataset = dataset.map(lambda x: {'text': x['text'], 'category': [cat for cat in x['category'] if cat not in discarded_categories]}, batched=False)
    dataset = dataset.filter(lambda x: len(x['category']) > 0)
    dataset = dataset.shuffle(seed=42).select(range(num_sample))

    # use clear_text to remove html tags
    dataset = dataset.map(lambda x: {'text': clear_text(x['text']), 'category': x['category']}, batched=False)
    dataset = dataset.filter(lambda x: len(x['text']) > 0)
    
    # parse categories, split by _, then extract by . and map each shortcut to long name
    categories = []
    for i in range(len(dataset)):
        categories.extend(dataset[i]['category'])
    categories = list(set(categories))
    # dataset = datasets.load_dataset("newsgroup", "20news")
    # dataset = dataset['test']

    
    return dataset, categories


if __name__ == "__main__":
    """
        Load all models and run a test on them.
    """
    models = list_all_models()

    # dataset, categories = load_news_category_dataset_v3(num_samples=200)
    dataset, categories = load_newsgroup_dataset(num_sample=1000)
    # dataset, categories = load_reuters_21578_dataset(num_samples=100)
    print(dataset.column_names)
    print(categories)

    #for example in dataset:
    #    print(example)

    # save dataset to disk
    # dataset.save_to_disk("newsgroup_dataset")

    # find_best_hypothesis_template(dataset, models, categories)
    
    #hypothesis_template = "This text examines the topic of {} in depth."
    # hypothesis_template = "The topic of this text is {}."
    hypothesis_template = "The text provides information about {}."                  # f1: 0.8340246, precision: 0.72866666, recall: 0.975
    hypothesis_template = "The text discusses {}."                                   # f1: 0.8653397, precision: 0.80166666, recall: 0.94
    hypothesis_template = "The text contains information relevant to {}."            # f1: 0.646798, precision: 0.4779761, recall: 1.0
    hypothesis_template = "The text provides insights into {}."                      # f1: 0.728584, precision: 0.5815956, recall: 0.975
    hypothesis_template = "The text sheds light on {}."                              # f1: 0.780856915458083, precision 0.60428, recall: 0.955
    hypothesis_template = "The text explores {} in detail."                          # f1: 0.8589041095890411, precision: 0.7837499999999998, recall: 0.95
    hypothesis_template = "The text provides a comprehensive analysis of {}."        # f1: 0.3638396560335281, precision: 0.34096825396825403, recall: 0.39
    hypothesis_template = "The text covers the topic of {} extensively."             # f1: 0.8264177721904259, precision: 0.7342777777777779, recall: 0.945
    hypothesis_template = "The text delves deeply into the topic of {}."             # f1: 0.854915042718633, precision: 0.7611666666666665, recall: 0.975
    hypothesis_template = "The text provides an in-depth look into the topic of {}." # f1: 0.6880380588451365, precision: 0.618623015873016, recall: 0.775
    hypothesis_template = "The example is about {}."                                 # f1: 0.8639711538461537, precision: 0.8183333333333332, recall: 0.915

    templates = [ "The text examines the topic of {} in depth.",
                    "The topic of this text is {}.",
                    "The text provides information about {}.",
                    "The text discusses {}.",
                    "The text contains information relevant to {}.",
                    "The text provides insights into {}.",
                    "The text sheds light on {}.",
                    "The text explores {} in detail.",
                    "The text provides a comprehensive analysis of {}.",
                    "The text covers the topic of {} extensively.",
                    "The text delves deeply into the topic of {}.",
                    "The example is about {}."]
    
    for i, template in enumerate(templates):
        print(f"Template: {template}")
        eval_model(models[3], dataset, categories, template, tag=f"{str(i)}")

    # eval_model(models[3], dataset, categories, hypothesis_template)

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

        
        


    