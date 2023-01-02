'''
    BDA - Project - Extraction of crypto wallet addresses from unstructured data sources.
    Author:         Michal Rein (xreinm00@stud.fit.vutbr.cz)
    File:           extractor.py
'''

import os
import pathlib
import re
import logging
import time
import shutil
from pathlib import Path
import tarfile
from multiprocessing import Process, Queue

IGNORE_EXTENSIONS_RE = [r'.*.js', r'.*.css', r'.*.jpg', r'.*.png', r'.*.svg', r'.*.gif', r'.*.ttf', r'.*.JPG']

# 30GB-200GB uncompressed
SKIP_FILES = ['evolution-forums.tar.xz', 'agora-forums.tar.xz', 'abraxas.tar.xz', 'agora.tar.xz', 'alphabay.tar.xz',
                'silkroad2-forums.tar.xz', 'evolution.tar.xz', 'silkroad2.tar.xz', 'blackbankmarket.tar.xz', 'outlawmarket.tar.xz', 'nucleus.tar.xz',
                'blackbankmarket-forums.tar.xz', 'thehub-forums.tar.xz', 'outlawmarket-forums.tar.xz', 'mtgox-20140309-leak.tar.xz']


# ETH, BTC, DASH, MONERO, Litecoin, BTCash
ADDRESSES_RE = [
    r'[ <>=",.]0x[a-fA-F0-9]{40}[ <>=",.]',
    r'[ <>=",.](?:[13]{1}[a-km-zA-HJ-NP-Z1-9]{26,33}|bc1[a-z0-9]{39,59})[ <>=",.]',
    r'[ <>=",.]X[1-9A-HJ-NP-Za-km-z]{33}[ <>=",.]',
    r'[ <>=",.]4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}[ <>=",.]',
    r'[ <>=",.][LM3][a-km-zA-HJ-NP-Z1-9]{26,33}[ <>=",.]',
    r'[ <>=",.][13][a-km-zA-HJ-NP-Z1-9]{33}[ <>=",.]']

ADDR_RE = re.compile(r'[ <>=",.](?:[13]{1}[a-km-zA-HJ-NP-Z1-9]{26,33}|bc1[a-z0-9]{39,59}|0x[a-fA-F0-9]{40}|X[1-9A-HJ-NP-Za-km-z]{33}|4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}|[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}|[13][a-km-zA-HJ-NP-Z1-9]{33})[ <>=",.]')

'''
    Worker target function for archive extraction.

        Parameters:
            name (int):         Worker identifier.
            job_queue (Queue):  Queue with directories which are ready for extraction.
            lists_path (str):   Path for storing path lists of interesting files.
'''
def find_interesting_stuff(name, job_queue: Queue, lists_path="./data"):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.info(f"Process {name}: starting...")
    
    found_paths = []
    while job_queue.qsize() != 0:
        path = job_queue.get(block=True)
        logging.info(f"Process {name}: Next job: {path}")
        for root, dirs, files in os.walk(path):
            root_path = pathlib.Path(root)
            for file in files:
                path = pathlib.Path(root_path, file)
                if any(re.match(regex, file) for regex in IGNORE_EXTENSIONS_RE):
                    continue
                try:
                    with open(path) as fp:
                        for line in fp.readlines():
                            line = line.replace('\n', ' ').replace('\t', '')
                            if re.search(ADDR_RE, line):
                                found_paths.append(str(path) + '\n')
                                continue

                except Exception as e:
                    pass

    logging.info(f"Process {name}: saving paths into file...")
    with open(f'{lists_path}/{name}.list', 'w+') as fp_out:
        fp_out.writelines(found_paths)

    logging.info("Process %s: finishing", name)


'''
    Extractor class definition.

        Parameters:
            num_of_workers (int):      Number of workers to be deployed for archive extraction.
'''
class DataExtractor():
    def __init__(self, num_of_workers=3) -> None:
        self.format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=self.format, level=logging.INFO, datefmt="%H:%M:%S")
        self.num_of_workers = num_of_workers

    '''
        Scan through given directory and subdirectories in parallel,
        find all interesting files and create path list to these files.
    '''
    def find_files_of_interest(self, root_dir, lists_path):
        queue = Queue(maxsize=1024)
        time.sleep(1)
        # Iterate over top-level directory, push all these dirs into queue.
        # All these directories will be processed in parallel.
        for root, dirs, files in os.walk(root_dir):
            if len(dirs) == 1: continue     
            for dir in dirs:
                queue.put(pathlib.Path(root, dir))
            break
        
        logging.info(f"Queue len: {queue.qsize()}")
        logging.info("Main    : creating workers.")

        workers: list[Process] = []
        for i in range(self.num_of_workers):
            x = Process(target=find_interesting_stuff, args=(i, queue, lists_path))
            workers.append(x)

        start = time.time()
        logging.info("Main    : Starting workers.")
        for i in range(self.num_of_workers):
            workers[i].start()

        logging.info("Main    : Wait for workers to finish.")
        for i in range(self.num_of_workers):
            workers[i].join()

        end = time.time()
        logging.info(f"Main    : all done, time: {end - start}s")
    
    '''
        Merge all path lists created by workers into one file.
    '''
    def merge_path_lists(self, lists_path) -> Path:
        assert Path(lists_path).is_dir()
        logging.info("Main    : Merging path lists created by workers...")

        all_paths_path = Path(f"{lists_path}/files_of_interest.list")
        with open(all_paths_path, "w+") as all_fp:
            for i in range(self.num_of_workers):
                with open(Path(f"{lists_path}/{i}.list")) as fp:
                    all_fp.writelines(fp.readlines())

        logging.info("Main    : Merging path lists complete...")
        return all_paths_path
    
    '''
        Copy directory structure of src_path into dest_path, then
        iterate over list of interesting files and copy them into dest_path
    '''
    def copy_interesting_files(self, src_path: Path, dest_path: Path, list_path=None):
        prefix = os.path.commonpath([src_path, dest_path])
        prefix_len = len(prefix) + len(os.path.sep)
        os.mkdir(Path(dest_path, src_path.name))
        try:
            # copy directory tree structure
            for root, dirs, files in os.walk(src_path):
                for dir in dirs:
                    dir_path = Path(dest_path, root[prefix_len:], dir)
                    os.mkdir(dir_path)
        except Exception as e:
            pass
        
        with open(list_path) as fp:
            for p in fp.readlines():
                path = p.replace('\n', '')
                shutil.copyfile(Path(path), Path(dest_path, path[prefix_len:]))


'''
    Run extractor on DNMArchives dataset. This dataset can be downloaded via:
    rsync --verbose --recursive rsync://176.9.41.242:873/dnmarchives/ ./dnmarchives/

        Parameters:
            dataset_path (str):         Path to dnmarchives directory.
            untar_archive_path (str):   Path where decompressed archives will be stored temporarily.
            copies_path (str):          Path to directory, where interesting files copies will be stored.
'''
def run_on_dnmarchives_dataset(dataset_path, untar_archive_path="./data", copies_path="./data/copies"):

    IGNORE_ARCHIVE_EXTS = [r'.*.sql.*', r'.*.xml.*', r'.*.sqlite.*', r'.*.par2', r'.*.csv.*', r'.*.mht', r'.*.mp3', r'.*.ogg', r'.*.docx']

    extractor = DataExtractor()
    failed = []
    failed_execptions = []
    # iterate over top level directory of the dataset, each file is .tar.xz archive
    for root, dirs, files in os.walk(dataset_path):
        root_path = Path(root)
        for file in files:
            try:
                path = Path(root_path, file)
                # skip any useless extensions
                if any(re.match(regex, file) for regex in IGNORE_ARCHIVE_EXTS):
                    continue

                # skip any large files for now
                if any(re.match(regex, file) for regex in SKIP_FILES):
                    continue

                print(f"File: {path}")
                basename = path.name
                basename_tar = path.stem
                basename_raw = basename_tar.split(".")[0]

                # copy already exists
                if os.path.exists(f"{copies_path}/{basename_raw}"): continue

                with tarfile.open(path, mode='r:xz', errorlevel=0) as tar_fp:
                    tar_fp.extractall(f'{untar_archive_path}/{basename_raw}')

                extractor.find_files_of_interest(f"{untar_archive_path}/{basename_raw}", untar_archive_path)
                extractor.merge_path_lists(f"{untar_archive_path}")
                extractor.copy_interesting_files(Path(f"{untar_archive_path}/{basename_raw}"), Path(f"{copies_path}"), Path(f'{untar_archive_path}/files_of_interest.list'))
                shutil.rmtree(f"{untar_archive_path}/{basename_raw}")
                print(f"Finished processing of {basename}")  

            except Exception as e:
                failed_execptions.append(e)
                continue
        
        for fail in failed:
            print(f"Failed to process: {fail}")
        
        for fail in failed_execptions:
            print("Exception occured:")
            print(fail)
        break
    
    print("Done.")

if __name__ == "__main__":
    run_on_dnmarchives_dataset("./data/dnmarchives/")


