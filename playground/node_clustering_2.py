import re
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from bs4 import BeautifulSoup

# Define a set of regular expressions that match common patterns in post or comment content
patterns = [
    r'\b(post|comment)\b',
    r'\bmessage\b',
    r'\bcontent\b',
    r'\bbody\b',
    r'\btext\b',
    r'\barticle\b',
    r'\bdescription\b',
    r'\bentry\b',
    r'\bopinion\b',
    r'\breview\b',
    r'\btestimonial\b'
]


# Define a set of non-structural tags that should be ignored
ignore_tags = ['a', 'link', 'html', 'head', 'body', 'meta', 'title', 'style', 'script', 'noscript', 'br', 'img', 'nav', 'header', 'form', 'footer', 'ul', 'li']



# Define a function that extracts text content from a BeautifulSoup node
def extract_text(node):
    return re.sub(r'\s+', ' ', node.text).strip()

# Define a function that computes a set of features for a given node
def compute_features(node):
    features = []
    # Extract tag name and class
    tag = node.name if node.name else ''
    class_ = ' '.join(node.get('class', []))
    features.extend([tag, class_])
    # Extract number of child nodes
    num_children = len(list(node.children))
    features.append(num_children)
    # Check for common patterns in text content
    text = extract_text(node)
    features.extend([int(bool(re.search(pattern, text))) for pattern in patterns])
    return features

# Define a function that trains a machine learning model to classify nodes as posts or comments
def train_model(nodes):
    # Extract features from all nodes
    X = [compute_features(node) for node in nodes]

    # Define target labels (1 for post or comment nodes, 0 for others)
    y = [1 if re.search(r'\b(post|comment)\b', extract_text(node), re.IGNORECASE) else 0 for node in nodes]

    # Train a Naive Bayes classifier on the features
    clf = MultinomialNB()
    clf.fit(X, y)

    return clf



# Define a function that applies the trained model to a new set of nodes and returns the top-ranked ones
def detect_nodes(nodes, clf, n=10):
    # Extract features from all nodes
    X = [compute_features(node) for node in nodes]

    # Use the classifier to predict the likelihood of each node being a post or comment
    y_pred = clf.predict_proba(X)[:, 1]

    # Sort nodes by predicted likelihood and return the top-ranked ones
    idx = np.argsort(y_pred)[::-1][:n]
    return [nodes[i] for i in idx]

if __name__ == "__main__":
    with open("/workspaces/webpage_categorization/data/bungee54-forums/bungee54-forums/2014-11-05/viewtopic.php_pid=4282", 'r') as f:
        html_content = f.read()

    # Example usage:
    # 1. Parse the HTML content of a webpage using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # 2. Extract all structural nodes that contain text content
    text_nodes = [node for node in soup.find_all() if node.text and not node.text.isspace() and node.name not in ignore_tags]

    # 3. Train a machine learning model on a subset of nodes that are known to be posts or comments (their class contains patterns like 'post' or 'comment')
    training_nodes_classes =  [node for node in text_nodes if re.search(r'\b.*(post|comment|message).*\b', " ".join(node.attrs.get('class', '')), re.IGNORECASE)]
    training_nodes_ids = [node for node in text_nodes if re.search(r'\b.*(post|comment|message).*\b', " ".join(node.attrs.get('id', '')), re.IGNORECASE)]
    # merge the two lists and remove duplicates
    training_nodes = list(set(training_nodes_classes + training_nodes_ids))
    clf = train_model(training_nodes)

    # 4. Use the trained model to detect the top-ranked nodes that are likely to be posts or comments
    post_nodes = detect_nodes(text_nodes, clf, n=10)