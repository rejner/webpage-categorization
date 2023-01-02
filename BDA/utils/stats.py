'''
    BDA - Project - Extraction of crypto wallet addresses from unstructured data sources.
    Author:         Michal Rein (xreinm00@stud.fit.vutbr.cz)
    File:           utils/stats.py
'''

import os
import re
from pathlib import Path

'''
    Count total size of dnmarchives files which have been already extracted.

        Parameters:
            dataset_path (str):         Path to dnmarchives directory.
            copies_path (str):          Path to directory, where interesting files copies are stored.

        Returns:
            total_size_archives (int): Total size of archives extracted in bytes.
'''
def count_dnmarchives_data_parsed(dataset_path, copies_path):
    IGNORE_ARCHIVE_EXTS = [r'.*.sql.*', r'.*.xml.*', r'.*.sqlite.*', r'.*.par2', r'.*.csv.*', r'.*.mht', r'.*.mp3', r'.*.ogg', r'.*.docx']
    parsed_dirs = os.listdir(copies_path)
    total_size_archives = 0
    for root, dirs, files in os.walk(dataset_path):
        root_path = Path(root)
        for file in files:
            path = Path(root_path, file)
            if any(re.match(regex, file) for regex in IGNORE_ARCHIVE_EXTS): continue
            basename_raw = path.name.split(".")[0]
            if basename_raw in parsed_dirs:
                total_size_archives += os.path.getsize(path)

    print(f"Total archive size: {total_size_archives} Bytes | {total_size_archives/1000000} MBs | {total_size_archives/1000000000} GBs")
    return total_size_archives

'''
    Count interesting files per archive.

        Parameters:
            copies_path (str):          Path to directory, where interesting files copies are stored.

        Returns:
            counts (dict <str, int>):   Dictionary with key-value pairs in format: {"<archive-name>": #files }
'''
def count_interesting_data_per_dir(copies_path, non_empty=False):
    total_files = 0
    dirs = os.listdir(copies_path)
    counts = {dir: 0 for dir in dirs}
    for dir in dirs:
        for root, dirs, files in os.walk(Path(copies_path, dir)):
            for file in files:
                path = Path(root, file)
                if os.path.isfile(path):
                    # print(file) 
                    total_files += 1
                    counts[dir] += 1

    # print results
    print(f"Total files: {total_files}")
    for key in counts.keys():
        if non_empty: 
            if counts[key] == 0: continue
        space_len = 50 - len(key)
        print(f"{key}:{' '*space_len} {counts[key]} files")

    return counts

if __name__ == "__main__":
    count_interesting_data_per_dir("data/copies")