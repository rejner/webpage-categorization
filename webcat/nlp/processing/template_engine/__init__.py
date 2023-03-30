from .chatGPT import ChatGPTTemplateEngine
from .k_means_clustering import KMeansClusteringTemplateEngine
from .most_elements_count import MostElementsCountTemplateEngine

def list_engines():
    return [
        ChatGPTTemplateEngine(),
        KMeansClusteringTemplateEngine(),
        MostElementsCountTemplateEngine(),
    ]