import bs4
from .base import TemplateEngine


class MostElementsCountTemplateEngine(TemplateEngine):
    def __init__(self):
        pass

    def template_from_file(self, file_path):
        raise NotImplementedError

    @property
    def name(self):
        return "Most Element Counts"
    
    @property
    def requiresKey(self):
        return False
    
    @property
    def description(self):
        return "This engine uses the most common element counts to create a template from a file."