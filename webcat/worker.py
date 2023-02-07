from webcat.nlp import WebCatNLP
from webcat.parser import WebCatParser

class WebCatWorker():
    def __init__(self) -> None:
        self.parser = WebCatParser()
        self.nlp = WebCatNLP()
    
    def process_files(self, files_path:list):
        contents = self.parser.parse_files(files_path)
        files_list = []
        categories_list = []
        text_list = []
        cnt = 0
        for file in contents:
            for text in contents[file]:
                categories = self.nlp.classify(text)
                entities, text = self.nlp.perform_NER(text)
                # split = text.split(" ")
                print("=====================================")
                print("File: ", file)
                # only categories with score > 0.7 (categories is a dict)
                # categories = {k: v for k, v in categories.items() if v > 0.5}
                print("Categories: ", categories)
                print(text)
                print("=====================================")
                files_list.append(file)
                categories_list.append(categories)
                text_list.append(text)
                cnt += 1
                if cnt > 10: break 
        return files_list, categories_list, text_list
    
    def process_files_batch(self, files_path:list, batch_size=4):
        contents = self.parser.parse_files(files_path)
        # merge all lists from contents dict into one
        contents = [item for sublist in contents.values() for item in sublist]

        files_list = []
        categories_list = []
        text_list = []
        cnt = 0
        # create iterator for the contents
        contents_iter = iter(contents)
        # get the first batch
        if len(contents) < batch_size:
            batch = contents
        else:
            batch = [next(contents_iter) for _ in range(batch_size)]
        
        while batch:
            categories = self.nlp.classify(batch)
            entities, texts = self.nlp.perform_NER(batch)
            files_list.extend(["file" for _ in range(batch_size)])
            categories_list.extend(categories)
            text_list.extend(texts)
            # get the next batch
            # catch StopIteration exception
            try:
                batch = [next(contents_iter) for _ in range(batch_size)]
            except StopIteration:
                batch = False
        return files_list, categories_list, text_list
 
    def process_raw_text(self, input: str):
        categories = self.nlp.classify(input)
        entities, text = self.nlp.perform_NER(input)
        return categories, text
    
    def set_hypothesis_template(self, hypothesis):
        self.nlp.set_hypothesis_template(hypothesis)

if __name__ == "__main__":
    worker = WebCatWorker()
    worker.process_batch([
        "data/abraxas-forums/abraxas-forums/2015-07-04/index.php_action=recent;start=10",
    ])
