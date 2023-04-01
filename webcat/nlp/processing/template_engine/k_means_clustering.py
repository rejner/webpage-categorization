import bs4
from .base import TemplateEngine


class KMeansClusteringTemplateEngine(TemplateEngine):
    def __init__(self):
        pass

    def template_from_file(self, file_path):
        raise NotImplementedError
    
    @property
    def name(self):
        return "K-Means Clustering"
    
    @property
    def requiresKey(self):
        return False
    
    @property
    def description(self):
        return "This engine uses K-Means Clustering to create a template from a file."
    
    