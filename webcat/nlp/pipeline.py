import sys
from os import path
sys.path.append(path.dirname(__file__))
sys.path.append(path.dirname(__file__) + "/.." + "/..")
from processing.parser import WebCatParser
from processing.analyzer import WebCatAnalyzer
import webcat.api.repositories.templates as t
import psycopg2
import timeit 
import multiprocessing as mp
import logging
import time

def producer_parser(queue, parser, file_paths):
    import os
    print('Starting producer => {}'.format(os.getpid()))
    # process files in the batches of 32
    batch_size = 32
    total = 0
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i+batch_size]

        print('Producer {} processing batch {}...'.format(os.getpid(), i))
        # process the batch
        contents = parser.parse_files(batch)

        print('Producer {} finished processing batch {}...'.format(os.getpid(), i))
        
        contents = [(file_path, text) for file_path, content in contents for text in content]
        # add the batch to the queue
        for content in contents:
            queue.put(content)
            total += 1

        print('Producer {} finished adding batch {} to the queue...'.format(os.getpid(), i))

    print('Producer {} exiting (produced {} files total)...'.format(os.getpid(), total))

def consumer_analyzer(queue, results_queue, lock, **kwargs):
    import os
    # Synchronize access to the console
    with lock:
        print('Starting consumer => {}'.format(os.getpid()))
    
    analyzer = WebCatAnalyzer()

    with lock:
        print('Consumer {} started...'.format(os.getpid()))

    # process the queue
    while True:
        # Synchronize access to the console
        with lock:
            print('Consumer {} waiting for items in the queue...'.format(os.getpid()))

        # take at most 16 items from the queue
        contents = []
        for i in range(16):
            try:
                contents.append(queue.get(timeout=1))
            except:
                break
        
        if len(contents) == 0:
            break
        
        # Synchronize access to the console
        with lock:
            print('Consumer {} processing item...'.format(os.getpid()))
        # process the item
        # contents = [(file_path, text) for file_path, content in contents for text in content]
        inputs = [content for _, content in contents]
        logging.info(f"Analyzing {len(inputs)} files")
        categories, entities, text =analyzer.analyze_content(inputs, **kwargs)
        if categories and entities and text:
            for i in range(len(contents)):
                results_queue.put({
                    "file": contents[i][0],
                    "categories": categories[i],
                    "entities": entities[i],
                    "text": text[i],
                    "raw_input": inputs[i]
                })

        # Synchronize access to the console
        with lock:
            print('Consumer {} finished processing item...'.format(os.getpid()))
        # indicate that the item has been processed
        
        # Synchronize access to the console
        with lock:
            print('Consumer {} finished processing item...'.format(os.getpid()))
 
    # Synchronize access to the console
    with lock:
        print('Consumer {} exiting...'.format(os.getpid()))
    
    exit(0)

class WebCatPipeline():
    def __init__(self):
        self.conn = psycopg2.connect(
            host="host.docker.internal",
            database="webcat_db",
            user='postgres',
            password='postgres',
            port=5432)
        templates = self.fetch_templates()
        self.parser = WebCatParser(templates)
        self.analyzer = WebCatAnalyzer()
        self.batch_size = 16
        self.max_queue_size = 1000
        self.queue = mp.Queue(maxsize=self.max_queue_size)

    def fetch_templates(self):
        self.templates_repo = t.TemplatesRepository(self.conn)
        templates = self.templates_repo.get_all()
        return templates

    def process_files(self, files_path:list, **kwargs):
        batch_size = kwargs.get("batch_size", self.batch_size) if "batch_size" in kwargs else self.batch_size
        contents = self.parser.parse_files(files_path)
        contents = [content for content in contents if content]
        # from (file_path, content (list of strings)) create a (file_path, content (string)) for each entry in contents
        # [(file_path, text), (file_path, text), ...]
        # create integer to path mapping to save memory when flattening the list and creating path-text pairs
        int_to_path = {i: file_path for i, (file_path, _) in enumerate(contents)}
        # invert the mapping to create a path to integer mapping
        path_to_int = {v: k for k, v in int_to_path.items()}

        contents = [(path_to_int[file_path], text) for file_path, content in contents for text in content]
        # create iterator for the contents
        contents_iter = iter(contents)

        batch = contents
        if len(contents) > batch_size:
            batch = [next(contents_iter) for _ in range(batch_size)]
        
        objects = []
        while batch:
            inputs = [content for _, content in batch]
            categories, entities, text = self.analyzer.analyze_content(inputs, **kwargs)
            if categories and entities and text: 
                for i in range(len(batch)):
                    objects.append({
                        "file": str(int_to_path[batch[i][0]]),
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
    
    def process_files_parallel(self, files_path:list, **kwargs):
        # spawn a new process, which takes all file paths
        # and parses them, putting the results in a queue
        p = mp.Process(target=producer_parser, args=(self.queue, self.parser, files_path))
        p.start()

        # wait for some samples in the queue
        while self.queue.qsize() < 1:
            print("Waiting for samples in the queue...")
            time.sleep(1)

        print("Starting analyzer...")
        results = []
        while True:
            # take at most 16 items from the queue
            contents = []
            for i in range(self.batch_size):
                try:
                    contents.append(self.queue.get(timeout=1))
                except:
                    break
            
            if len(contents) == 0:
                break
            
            # process the item
            # contents = [(file_path, text) for file_path, content in contents for text in content]
            inputs = [content for _, content in contents]
            logging.info(f"Analyzing {len(inputs)} files")
            categories, entities, text = self.analyzer.analyze_content(inputs, **kwargs)
            if categories and entities and text:
                for i in range(len(contents)):
                    results.append({
                        "file": contents[i][0],
                        "categories": categories[i],
                        "entities": entities[i],
                        "text": text[i],
                        "raw_input": inputs[i]
                    })
        
        print(len(results))
        return results


    def process_raw_text(self, text, **kwargs):
        categories, entities, text = self.analyzer.analyze_content([text], **kwargs)
        return {
            "categories": categories[0],
            "entities": entities[0],
            "text": text[0]
        }
    
if __name__ == "__main__":
    pipeline = WebCatPipeline()
    import os
    # data = pipeline.process_files(
    #     ["/workspaces/webpage_categorization/data/bungee54-forums/bungee54-forums/2014-11-05/viewtopic.php_pid=4282"]
    # )
    # print(data)
    # 10
    # list directory
    root_dir = "/workspaces/webpage_categorization/data/parallel_test"
    files = os.listdir(root_dir)
    files = [os.path.join(root_dir, file) for file in files]
    print(f"Time to process 1 file with sync: {timeit.timeit(lambda: pipeline.process_files(files), number=1)}")
    # print(f"Time to process 1 file with async: {timeit.timeit(lambda: pipeline.process_files_parallel(files), number=1)}")
    #timeit.timeit(lambda: pipeline.process_files(["/workspaces/webpage_categorization/data/bungee54-forums/bungee54-forums/2014-11-05/viewtopic.php_pid=4282"]), number=1,)



# import sys
# from os import path
# sys.path.append(path.dirname(__file__))
# sys.path.append(path.dirname(__file__) + "/.." + "/..")
# from processing.parser import WebCatParser
# from processing.analyzer import WebCatAnalyzer
# import webcat.api.repository.templates as t
# import psycopg2

# class WebCatPipeline():
#     def __init__(self):
#         self.conn = psycopg2.connect(
#             host="host.docker.internal",
#             database="webcat_db",
#             user='postgres',
#             password='postgres',
#             port=5432)
#         templates = self.fetch_templates()
#         self.parser = WebCatParser(templates)
#         self.analyzer = WebCatAnalyzer()
#         self.batch_size = 32

#     def fetch_templates(self):
#         self.templates_repo = t.TemplatesRepository(self.conn)
#         templates = self.templates_repo.get_all()
#         return templates

#     def process_files(self, files_path:list, **kwargs):
#         batch_size = kwargs.get("batch_size", self.batch_size) if "batch_size" in kwargs else self.batch_size
#         contents = self.parser.parse_files(files_path)
#         # from (file_path, content (list of strings)) create a (file_path, content (string)) for each entry in contents
#         # [(file_path, text), (file_path, text), ...]
#         # create integer to path mapping to save memory when flattening the list and creating path-text pairs
#         int_to_path = {i: file_path for i, (file_path, _) in enumerate(contents)}
#         # invert the mapping to create a path to integer mapping
#         path_to_int = {v: k for k, v in int_to_path.items()}

#         contents = [(path_to_int[file_path], text) for file_path, content in contents for text in content]
#         # create iterator for the contents
#         contents_iter = iter(contents)

#         batch = contents
#         if len(contents) > batch_size:
#             batch = [next(contents_iter) for _ in range(batch_size)]
        
#         objects = []
#         while batch:
#             inputs = [content for _, content in batch]
#             categories, entities, text = self.analyzer.analyze_content(inputs, **kwargs)
#             for i in range(len(batch)):
#                 objects.append({
#                     "file": str(int_to_path[batch[i][0]]),
#                     "categories": categories[i],
#                     "entities": entities[i],
#                     "text": text[i],
#                     "raw_input": inputs[i]
#                 })
#             try:
#                 batch = [next(contents_iter) for _ in range(batch_size)]
#             except StopIteration:
#                 batch = False
#         return objects


#     def process_raw_text(self, text, **kwargs):
#         categories, entities, text = self.analyzer.analyze_content([text], **kwargs)
#         return {
#             "categories": categories[0],
#             "entities": entities[0],
#             "text": text[0]
#         }
    
# if __name__ == "__main__":
#     pipeline = WebCatPipeline()
#     data = pipeline.process_files(
#         ["/workspaces/webpage_categorization/data/bungee54-forums/bungee54-forums/2014-11-05/viewtopic.php_pid=4282"]
#     )
#     print(data)
