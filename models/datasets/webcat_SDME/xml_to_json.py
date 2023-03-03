import json
from bs4 import BeautifulSoup
import re
import random

"""
    Dataset format:
    <dataset>
        <s>Entry 1</s>
        <s>Entry 2</s>
        <s>Entry 3</s>
        ...
    </dataset>
"""

id_to_label_mapping = {
    0: "O", 1: "B-PER", 2: "I-PER", 3: "B-ORG", 
    4:"I-ORG", 5: "B-LOC", 6: "I-LOC", 7: "B-MISC",
    8: "I-MISC", 9: "B-PROD", 10: "I-PROD", 11: "B-WALLET"
}

# crypto address prefixes
address_prefixes = ['0x', 'bc1', '3', 'bcrt1', 'tb1', '2', '1', 'm', 'n', '2N']

def is_substring_in_tokens(entity, tokens):
    index = None
    for token in tokens:
        if entity in token:
            index = tokens.index(token)
            break
    return index

def find_entity_index(entity, tokens):
    try:
        index = tokens.index(entity)
    except:
        index = is_substring_in_tokens(entity, tokens)
    return index


def parse_sample(entry):
    """
    Parse a entry from the dataset containing entities also in XML tags.
    XML tags: <username>, <organization>, <location>
    """
    text = entry.text
    # split text into tokens, separated by commas or spaces and keep the separators
    # e.g. "Hello, world!" -> ["Hello", ",", "world!"]
    tokens = re.split(r"(\s|[,.?!])", text) # tokens = re.split(r"[\s,.]+", text)
    # remove empty tokens
    tokens = [token for token in tokens if token != "" and token != " "]


    tags = [0] * len(tokens)
    contents = entry.contents
    for content in contents:
        if content.name == "username":
            # text can be multiple tokens, first token in a B-PER tag, the rest I-PER
            if len(content.text.split()) > 1:
                # first token
                index = find_entity_index(content.text.split()[0], tokens)
                if index is None:
                    continue
                tags[index] = 1
                # rest of tokens
                for token in content.text.split()[1:]:
                    index += 1
                    tags[index] = 2
            else:
                index = find_entity_index(content.text, tokens)
                if index is None:
                    continue
                tags[index] = 1

        elif content.name == "organization":
            # text can be multiple tokens, first token in a B-ORG tag, the rest I-ORG
            if len(content.text.split()) > 1:
                index = find_entity_index(content.text.split()[0], tokens)
                if index is None:
                    continue
                tags[index] = 3
                # rest of tokens
                for token in content.text.split()[1:]:
                    index += 1
                    tags[index] = 4
            else:
                index = find_entity_index(content.text, tokens)
                if index is None:
                    continue
                tags[index] = 3
            
        elif content.name == "location":
            # text can be multiple tokens, first token in a B-LOC tag, the rest I-LOC
            if len(content.text.split()) > 1:
                index = find_entity_index(content.text.split()[0], tokens)
                if index is None:
                    continue
                tags[index] = 5

                # rest of tokens
                for token in content.text.split()[1:]:
                    index += 1
                    tags[index] = 6
                
            else:
                index = find_entity_index(content.text, tokens)
                if index is None:
                    continue
                tags[index] = 5
            
        elif content.name == "wallet":
            # inside this tag, placeholder ADDRESS is used
            # Generate a random address (hash) and replace ADDRESS with it inside tokens
            index = find_entity_index(content.text, tokens)
            if index is None:
                continue
            random_index = random.randint(0, len(address_prefixes) - 1)
            # random length of address (26-35) characters
            address_hash = address_prefixes[random_index] + ''.join(random.choice('0123456789abcdef') for i in range(random.randint(26, 35)))
            tokens[index] = address_hash
            tags[index] = 11
       
        elif content.name == "product":
            # text can be multiple tokens, first token in a B-PROD tag, the rest I-PROD
            if len(content.text.split()) > 1:
                index = find_entity_index(content.text.split()[0], tokens)
                if index is None:
                    continue
                tags[index] = 9

                # rest of tokens
                for token in content.text.split()[1:]:
                    index += 1
                    tags[index] = 10
            else:
                index = find_entity_index(content.text, tokens)
                if index is None:
                    continue
                tags[index] = 9

    
    return {
        "tokens": tokens,
        "tags": tags
    }

def xml_to_json(xml_file, json_path):
    with open(xml_file) as f:
        soup = BeautifulSoup(f, "xml")
        dataset = []
        for entry in soup.find_all("s"):
            e = parse_sample(entry)
            dataset.append(e)
        
        splits = [0.8, 0.1, 0.1]
        for i, file in enumerate(['train.json', 'dev.json', 'test.json']):
            json_file = json_path + file
            # split dataset into train, dev and test
            subset = dataset[int(sum(splits[:i]) * len(dataset)):int(sum(splits[:i+1]) * len(dataset))]
            with open(json_file, "w") as f:
                # write each entry in a new line
                for entry in subset:
                    f.write(json.dumps(entry) + "\n")
            
    

if __name__ == "__main__":
    xml_file = "/workspaces/webpage_categorization/models/datasets/webcat_SDME/generated_dataset.xml"
    json_path = "/workspaces/webpage_categorization/models/datasets/webcat_SDME/"
    xml_to_json(xml_file, json_path)
