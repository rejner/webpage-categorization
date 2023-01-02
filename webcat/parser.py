from pathlib import Path
import logging
from bs4 import BeautifulSoup
import pandas as pd
import re

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

    def parse_files(self, files_path:list):
        contents = {}
        for file in files_path:
            path = Path(file)
            logging.info(f"Parsing file: {path}")
            texts = self._parse_file(path)
            contents[file] = texts
        return contents

    '''
        Parse given file with a set of tools and create data object.
    '''
    def _parse_file(self, file_path: Path):
        with open(file_path) as fd:
            texts = []
            try:
                contents = fd.read()
                self.process_all_tables(contents)
                soup = BeautifulSoup(contents, features="html.parser")
                
                # get rid of scirpt/style and table tags
                for unnecessary in soup(["script", "style", "nav", "table", "header"]):
                    unnecessary.extract()
            
                # Find all the tags in the Beautiful Soup object
                tags = soup.find_all()

                # Initialize a variable to keep track of the tag with the most children
                most_children = None
                max_children = 0

                # Iterate over all the tags
                for tag in tags:
                    # Count the number of children of the current tag
                    num_children = len(list(tag.children))
                
                    # If the current tag has more children than the current maximum, update the maximum
                    if num_children == 111:
                        print(tag)
                    if num_children > max_children:
                        max_children = num_children
                        most_children = tag
                
                for child in most_children.children:
                    if not child.name: # ignore comments
                        continue
                    # remove all children with class button in it
                    # get all children with class button
                    buttons = child.find_all(class_=re.compile
                    ("button"))
                    # remove all children with class button
                    for button in buttons:
                        button.decompose()

                    # get text from the tag
                    text = child.text
                    # strip the text
                    text = text.strip()
                    # remove newlines
                    text = text.replace("\n", " ")
                    # remove multiple spaces
                    text = " ".join(text.split())
                    if text != "":
                        # count word count in tex
                        word_count = len(text.split())
                        # if word count is more than 256, then split the text into 256 words,
                        # split text into multiple 256 blocks
                        if word_count > 256:
                            # split text into 256 words
                            text = text.split()
                            # split text into 256 words
                            text = [text[i:i+256] for i in range(0, len(text), 256)]
                            # join the text
                            text = [" ".join(t) for t in text]

                        if isinstance(text, list):
                            texts.extend(text)
                        else:
                            texts.append(text)

            except Exception as e:
                logging.info(f"{e}")
            
            print(texts)
            
            return texts

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
    parser = WebCatParser()
    # directory = "D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04"
    # files = os.listdir('D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04')
    # files = [os.path.join(directory, filename) for filename in files]
    # analyzer.analyze_files(files)
    # exit(0)
    parser.parse_files([
        "data/abraxas-forums/abraxas-forums/2015-07-04/index.php_action=recent;start=10",
        # "D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04\index.php_action=mlist;sa=all;start=e",
        # "D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04\index.php_topic=1197.0",
        # "D:\FIT-VUT\DP\webpage_categorization\data\\abraxas-forums\\abraxas-forums\\2015-07-04\index.php_topic=904.1200"
        ])


    
