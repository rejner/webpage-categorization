from .chatGPT import ChatGPTTemplateEngine
from .k_means_clustering import KMeansClusteringTemplateEngine
from .most_elements_count import MostElementsCountTemplateEngine
from .chatGPT_v2 import ChatGPTTemplateEngine_v2

def list_engines():
    return [
        ChatGPTTemplateEngine_v2(),
        ChatGPTTemplateEngine(),
        KMeansClusteringTemplateEngine(),
        MostElementsCountTemplateEngine()
    ]