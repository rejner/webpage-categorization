from nlp.pipeline import WebCatPipeline
import os
import logging

class WebCatWorker():
    def __init__(self, db):
        self.pipeline = None
        self.db = db
    
    def create_files_list(self, path:str, **kwargs):
        logging.info("Creating files list from path: {}".format(path))
        recursive = kwargs.get("recursive", False)
        # if path is a file, return it
        if os.path.isfile(path):
            return [path]
        
        # if path is a directory, return all files in it
        # if recursive is True, return all files in all subdirectories
        files = []
        if os.path.isdir(path):
            if not recursive:
                for filename in os.listdir(path):
                    file_path = os.path.join(path, filename)
                    if os.path.isfile(file_path):
                        files.append(file_path)
            else:
                for root, dirs, files in os.walk(path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        files.append(file_path)

            logging.info("Found {} files in path: {}".format(len(files), path))
            return files
        
        raise Exception("Path is not a file or directory")
        

    # def process_files(self, files_path:list, **kwargs):
    #     if self.pipeline is None:
    #         self.pipeline = WebCatPipeline(self.db)
    #     file_paths = self.create_files_list(files_path, **kwargs)
    #     return self.pipeline.process_files(file_paths, **kwargs)
    
    def process_files(self, files_path:list, **kwargs):
        if self.pipeline is None:
            self.pipeline = WebCatPipeline(self.db)
        file_paths = self.create_files_list(files_path, **kwargs)
        # r1 = self.pipeline.process_files(file_paths, **kwargs)
        # if len(file_paths) > 10000:
        #     file_paths = file_paths[8800:8900]
        r1 = self.pipeline.process_files_as_dataset(file_paths, **kwargs)
        return r1

    def process_raw_text(self, text: str, **kwargs):
        if self.pipeline is None:
            self.pipeline = WebCatPipeline(self.db)
        return self.pipeline.process_raw_text(text, **kwargs)

# worker = WebCatWorker()

if __name__ == "__main__":
    worker = WebCatWorker()
    worker.process_files([
        "data/abraxas-forums/abraxas-forums/2015-07-04/index.php_action=recent;start=10",
        "/workspaces/webpage_categorization/data/bungee54-forums/bungee54-forums/2014-11-05/viewtopic.php_pid=4282",
    ])
    #print(data)
