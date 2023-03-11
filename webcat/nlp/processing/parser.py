from pathlib import Path
import logging
import pandas as pd
import re
from .parsing_strategy import HighestChildrenFrequencyStrategy
from .parsing_strategy import StoredTemplatesStrategy

url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
email_pattern = r'[\w\.-]+@[\w\.-]+'

'''
    WebCatParser class definition.
    The parser is responsible for parsing the HTML files and extracting the data.
        Parameters:
            files_path (list[str]):      Path(s) to files which should be analyzed
            timeout (int):               Time limit in seconds for parsing a file.
'''
class WebCatParser():
    def __init__(self, timeout=10) -> None:
        self.format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=self.format, level=logging.INFO, datefmt="%H:%M:%S")
        self.timeout = timeout
        self.strategy = StoredTemplatesStrategy()
        self.fallback_strategy = HighestChildrenFrequencyStrategy()

    def parse_files(self, files_path:list):
        """
            Parse given files with a set of tools and create data object, where each
            file is a key and its content split into segments of text data is a value.
        """
        contents = {}
        for file in files_path:
            path = Path(file)
            logging.info(f"Parsing file: {path}")
            chunks = self._parse_file(path)
            contents[file] = chunks
        return contents

    '''
        Parse given file with a set of tools and create data object.
    '''
    def _parse_file(self, file_path: Path):
        try:
            with open(file_path) as fd:
                contents = fd.read()
                chunks = self.strategy.parse(contents)
                # self.process_all_tables(contents)
                chunks  = [self.clear_text(chunk) for chunk in chunks ]
                return chunks 
            
        except Exception as e:
            logging.info(f"{e}")

    '''
        Process all tables with pandas library, remove empty columns.
    '''
    def process_all_tables(self, contents):
        try:
            df_list = pd.read_html(contents) # this parses all the tables in webpages to a list
            for df in df_list:
                df = df.dropna(axis=1, how='all') # drop columns with all NaN values
                print(df.head())

        except Exception as e:
            logging.info(f"{e}")


    def clear_text(self, text):
        # remove urls
        # urls = re.findall(url_pattern, text)
        text = re.sub(url_pattern, '', text)
        # remove emails
        # emails = re.findall(email_pattern, text)
        text = re.sub(email_pattern, '', text)
        # remove html tags
        text = re.sub(r'<[^>]*>', '', text)
        return text


if __name__ == "__main__":
    parser = WebCatParser()
    # directory = "D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04"
    # files = os.listdir('D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04')
    # files = [os.path.join(directory, filename) for filename in files]
    # analyzer.analyze_files(files)
    # exit(0)
    contents = parser.parse_files([
        "data/abraxas-forums/abraxas-forums/2015-07-04/index.php_action=recent;start=10",
        # "D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04\index.php_action=mlist;sa=all;start=e",
        # "D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04\index.php_topic=1197.0",
        # "D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04\index.php_topic=904.1200"
        ])
    print(contents)


    
