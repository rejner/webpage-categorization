import os
from pathlib import Path
import logging
from bs4 import BeautifulSoup
import pandas as pd
from nlp import WebCatNLP
import numpy as np

'''
    Analyzer class definition.
        Parameters:
            files_path (list[str]):      Path(s) to files which should be analyzed
            timeout (int):               Time limit in seconds for parsing a file.
'''
class Analyzer():
    def __init__(self, timeout=10) -> None:
        self.format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=self.format, level=logging.INFO, datefmt="%H:%M:%S")
        self.timeout = timeout
        self.nlp = WebCatNLP()

    def analyze_files(self, files_path:list):
        for file in files_path:
            path = Path(file); logging.info(f"Parsing file: {path}")
            self.parse_file(path)

    '''
        Parse given file with a set of tools and create data object.
    '''
    def parse_file(self, file_path: Path):
        with open(file_path) as fd:
            try:
                contents = fd.read()
                self.process_all_tables(contents)
                soup = BeautifulSoup(contents, features="html.parser")
                
                # get rid of scirpt/style and table tags
                for unnecessary in soup(["script", "style", "nav", "table"]):
                    unnecessary.extract() 

                text = soup.get_text(strip=True, separator=' ')  
                ner_res = self.nlp.perform_ner_tner(text)
                print(ner_res['entity_prediction'][0])
                print(text)

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


if __name__ == "__main__":
    analyzer = Analyzer()
    # directory = "D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04"
    # files = os.listdir('D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04')
    # files = [os.path.join(directory, filename) for filename in files]
    # analyzer.analyze_files(files)
    # exit(0)
    analyzer.analyze_files([
        "data/abraxas-forums/abraxas-forums/2015-07-04/index.php_action=recent;start=10",
        # "D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04\index.php_action=mlist;sa=all;start=e",
        # "D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04\index.php_topic=1197.0",
        # "D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04\index.php_topic=904.1200"
        ])
    
