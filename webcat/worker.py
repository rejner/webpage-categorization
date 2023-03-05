from nlp.pipeline import WebCatPipeline
import os

class WebCatWorker():
    def __init__(self):
        self.pipeline = WebCatPipeline()
    
    def create_files_list(self, path:str, **kwargs):
        recursive = kwargs.get("recursive", False)
        # if path is a file, return it
        if os.path.isfile(path):
            return [path]
        
        # if path is a directory, return all files in it
        # if recursive is True, return all files in all subdirectories
        files = []
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    files.append(os.path.join(root, file))
                if not recursive:
                    break
            return files
        
        raise Exception("Path is not a file or directory")
        

    def process_files(self, files_path:list, **kwargs):
        files = self.create_files_list(files_path, **kwargs)
        return self.pipeline.process_files(files, **kwargs)
 
    def process_raw_text(self, text: str, **kwargs):
        return self.pipeline.process_raw_text(text, **kwargs)

if __name__ == "__main__":
    worker = WebCatWorker()
    worker.process_files([
        "data/abraxas-forums/abraxas-forums/2015-07-04/index.php_action=recent;start=10",
        "/workspaces/webpage_categorization/data/bungee54-forums/bungee54-forums/2014-11-05/viewtopic.php_pid=4282",
    ])
    #print(data)
