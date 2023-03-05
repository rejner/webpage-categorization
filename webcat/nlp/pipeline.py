import sys
from os import path
sys.path.append(path.dirname(__file__))
from processing.parser import WebCatParser
from processing.analyzer import WebCatAnalyzer

class WebCatPipeline():
    def __init__(self):
        self.parser = WebCatParser()
        self.analyzer = WebCatAnalyzer()
        self.batch_size = 4

    def process_files(self, files_path:list, **kwargs):
        batch_size = kwargs.get("batch_size", self.batch_size) if "batch_size" in kwargs else self.batch_size
        contents_parsed = self.parser.parse_files(files_path)
        # merge all lists from contents dict into one
        # contents = [item for sublist in contents_parsed.values() for item in sublist]
        contents = [(file, content_part) for file, content in contents_parsed.items() for content_part in content]

        # create iterator for the contents
        contents_iter = iter(contents)
        # get the first batch
        if len(contents) < batch_size:
            batch = contents
        else:
            batch = [next(contents_iter) for _ in range(batch_size)]
        
        objects = []
        while batch:
            inputs = [content for _, content in batch]
            categories, entities, text = self.analyzer.analyze_content(inputs, **kwargs)
            for i in range(len(batch)):
                objects.append({
                    "file": batch[i][0],
                    "categories": categories[i],
                    "entities": entities[i],
                    "text": text[i],
                    "raw_input": inputs[i]
                })
            try:
                batch = [next(contents_iter) for _ in range(batch_size)]
            except StopIteration:
                batch = False
        return objects


    def process_raw_text(self, text, **kwargs):
        categories, entities, text = self.analyzer.analyze_content([text], **kwargs)
        return {
            "categories": categories[0],
            "entities": entities[0],
            "text": text[0]
        }
    
if __name__ == "__main__":
    pipeline = WebCatPipeline()
    data = pipeline.process_files(
        ["data/abraxas-forums/abraxas-forums/2015-07-04/index.php_action=recent;start=10"]
    )
    print(data)

