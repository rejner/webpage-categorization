from pathlib import Path
import logging
import re
import sys
import os
import joblib
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from .parsing_strategy import TemplatesStrategy, ParsingStrategy, ConfigMappingStrategy
from .parsing_strategy.exceptions import NoParsableContentError
from webcat.models_extension import Template

logging.basicConfig(level=logging.DEBUG)
url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
email_pattern = r'[\w\.-]+@[\w\.-]+'


def mock_parse_file(file_path: Path):
    logging.info(f"Parsing file: {file_path}")
    return None

'''
    WebCatParser class definition.
    The parser is responsible for parsing the HTML files and extracting the data.
        Parameters:
            files_path (list[str]):      Path(s) to files which should be analyzed
            timeout (int):               Time limit in seconds for parsing a file.
'''
class WebCatParser():
    def __init__(self, db, **kwargs):
        self.format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=self.format, level=logging.DEBUG, datefmt="%H:%M:%S")
        self.db = db
        file_type = kwargs.get("file_type", "txt")

        if file_type == "html":
            templates = self.fetch_templates()
            self.strategy = TemplatesStrategy(templates)
        
        if file_type == "csv":
            mapping = kwargs.get("mapping", None)
            self.strategy = ConfigMappingStrategy(mapping)
        
        if file_type == "txt":
            self.strategy = ParsingStrategy()

    def fetch_templates(self):
        templates = []
        templates = self.db.session.query(Template).all()
        templates = [template.json_serialize() for template in templates]
        return templates        

    def parse_files(self, file_paths:list):
        """
            Parse given files with a set of tools and create data object, where each
            file is a key and its content split into segments of text data is a value.
        """
        contents = {}

        # if only one file is given, do not use joblib
        if len(file_paths) == 1:
            path = Path(file_paths[0])
            contents = [parse_file(path, self.strategy)]
            contents = [item for item in contents if item is not None]
            return contents
        
        # use joblib to parallelize the parsing process (returns a list of tuples, where each tuple is (file_path, list of strings (texts))
        contents = joblib.Parallel(n_jobs=-1, verbose=1)(joblib.delayed(parse_file)(file, self.strategy) for file in file_paths)
        contents = [item for item in contents if item is not None]
        return contents

    def parse_raw_text(self, text):
        text = self.strategy.clear_text(text)
        return text

    
'''
    Parse given file with a set of tools and create data object.
'''
def parse_file(file_path: Path, strategy: ParsingStrategy):
    logging.info(f"Parsing file: {file_path}")
    try:
        chunks = strategy.parse(file_path)
        return chunks

    except Exception as e:
        logging.info(f"No parsable content found in file: {file_path}")
        logging.info(e)
        return None