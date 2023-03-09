from bs4 import BeautifulSoup
from sklearn.cluster import KMeans
from sklearn.feature_extraction import DictVectorizer
import re
import nltk
import datetime
nltk.download('punkt')
nltk.download('stopwords')
import matplotlib.pyplot as plt
import time

def preprocess_soup(soup):
    # remove script and style elements
    for tag in soup(["script", "style", "noscript", "br", "img", "nav", "header"]):
        tag.extract()    # rip it out
    return soup

def extract_element_features(element, total_text_length=None):
    features = {
        'tag': element.name,
        'class': element.get('class', []),
        'id': element.get('id', []),
    }
    if features['tag'] in ['a', 'link', 'html', 'head', 'body', 'meta', 'title', 'style', 'script', 'noscript', 'br', 'img', 'nav', 'header']:
        return None
 
    # features['level_1_children_tags'] = [child.name for child in element.children if child.name]
    features['descendants_tags'] = [child.name for child in element.descendants if child.name]
    # features['descendants_tags'] = list(set(features['descendants_tags']))
    # sort the tags alphabetically
    features['descendants_tags'] = sorted(features['descendants_tags'])
    features['descendants_tags'] = list(set(features['descendants_tags']))
    features['descendants_classes'] = [child.get('class', []) for child in element.descendants if child.name]
    # flatten the list of lists
    features['descendants_classes'] = [item for sublist in features['descendants_classes'] for item in sublist]
    # sort the classes alphabetically
    features['descendants_classes'] = sorted(features['descendants_classes'])
    features['descendants_classes'] = list(set(features['descendants_classes']))
    # features['descendants_ids'] = [child.get('id', []) for child in element.descendants if child.name]
    # flatten the list of lists
    # features['descendants_ids'] = [item for sublist in features['descendants_ids'] for item in sublist]
    # sort the ids alphabetically
    # features['descendants_ids'] = sorted(features['descendants_ids'])
    # get text from element which is not part of children
    #text = element.get_text()
    # tokenize the text, remove punctuation and stopwords
    #tokens = nltk.word_tokenize(text)
    #tokens = [token for token in tokens if re.match(r'\w+', token)]
    #tokens = [token for token in tokens if token not in nltk.corpus.stopwords.words('english')]
    # sort the tokens alphabetically
    # features['tokens'] = tokens
    parents = [parent.name for parent in element.parents]
    features['depth'] = len(parents)
    features['num_children'] = len(list(element.children))
    # get text length
    features['text_length'] = len(element.get_text()) / total_text_length


    

    return features

def detect_repeating_patterns(html, n_clusters=20):
    soup = BeautifulSoup(html, 'html.parser')
    soup = preprocess_soup(soup)

    elements = soup.find_all()
    text_length = len(soup.get_text())
    element_features = [extract_element_features(element, text_length) for element in elements]
    element_features = [feature for feature in element_features if feature]
    vectorizer = DictVectorizer()
    element_feature_matrix = vectorizer.fit_transform(element_features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(element_feature_matrix)
    clusters = kmeans.predict(element_feature_matrix)

    #for i, cluster in enumerate(clusters):
    #    print(f"Element {i} is in cluster {cluster}")
    
    # now create 10 bins of elements
    bins = [[] for _ in range(n_clusters)]
    for i, cluster in enumerate(clusters):
        bins[cluster].append(element_features[i])
    
    # now print out the elements in each bin, just 3 elements per bin
    # for i, bin in enumerate(bins):
    #     print(f"Bin {i} has {len(bin)} elements")
    #     for element in bin[:3]:
    #         print(element)
    #         print()
    visualize_bins(kmeans, vectorizer, clusters, bins)
    print("Hello")


def visualize_bins(kmeans, vectorizer: DictVectorizer, clusters, bins):
    # keep only bins with more than 1 element and div elements in them
    # for now, get indices only
    bins_indices = [i for i, bin in enumerate(bins) if len(bin) > 1 and any([feature['tag'] == 'div' for feature in bin])]
    # get centroids
    centroids = kmeans.cluster_centers_
    # keep only the centroids that are in bins with more than 1 element
    centroids = centroids[bins_indices]
    bins = [bins[i] for i in bins_indices]

    # get the feature names
    feature_names = vectorizer.feature_names_
    # get the number of elements in each cluster
    cluster_sizes = [len(bin) for bin in bins]

    # plot centroids on 2D plane using PCA
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    pca.fit(centroids)
    centroids_2d = pca.transform(centroids)

    # plot the centroids
    plt.scatter(centroids_2d[:, 0], centroids_2d[:, 1], marker='x', color='red')
    # plot the cluster sizes
    plt.scatter(centroids_2d[:, 0], centroids_2d[:, 1], s=cluster_sizes, alpha=0.5)
    # plot the cluster labels
    for i, centroid in enumerate(centroids_2d):
        plt.text(centroid[0], centroid[1], str(i))
    
    # create timestamp in format 2020-01-01_00-00-00
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    plt.savefig(f"/workspaces/webpage_categorization/images/cluster_sizes_{timestamp}.png")
    plt.show()




if __name__ == "__main__":
    # with open("data/bungee54-forums/bungee54-forums/2014-11-05/viewtopic.php_pid=4282", 'r') as f:
    #     html = f.read()
    #     detect_repeating_patterns(html)
    with open("/workspaces/webpage_categorization/data/abraxas-forums/abraxas-forums/2015-07-04/index.php_topic=390.0", 'r') as f:
        html = f.read()
        detect_repeating_patterns(html, n_clusters=10)