'''
    BDA - Project - Extraction of crypto wallet addresses from unstructured data sources.
    Author:         Michal Rein (xreinm00@stud.fit.vutbr.cz)
    File:           parser.py
'''

import os
import string
from pathlib import Path
import logging
import re
from bs4 import BeautifulSoup
import json
import hashlib
import nltk
from nltk.corpus import words
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from utils.timeout import time_limit, TimeoutException

PURE_ADDR_RE = re.compile(r'(?:[13]{1}[a-km-zA-HJ-NP-Z1-9]{26,33}|bc1[a-z0-9]{39,59}|0x[a-fA-F0-9]{40}|X[1-9A-HJ-NP-Za-km-z]{33}|4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}|[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}|[13][a-km-zA-HJ-NP-Z1-9]{33})')

# ETH, BTC, DASH, MONERO, Litecoin, BTCash
ADDRESSES_RE = [
    r'0x[a-fA-F0-9]{40}',
    r'(?:[13]{1}[a-km-zA-HJ-NP-Z1-9]{26,33}|bc1[a-z0-9]{39,59})',
    r'X[1-9A-HJ-NP-Za-km-z]{33}',
    r'4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}',
    r'[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}',
    r'[13][a-km-zA-HJ-NP-Z1-9]{33}']
ADDRESSES_ENUM = ['ethereum', 'bitcoin', 'dash', 'monero', 'litecoin', 'bitcoin cash']

USERS_RE = re.compile('[uU]ser.*')

EXCLUDE_WORDS = ['username', 'user', 'users', 'online', 'btc', 'bitcoin', 'http', 'unix', 'update', 'logout', 'updated', 'pgp',
                 'arrive', 'info', 'strong', 'Ive', 'Europe', 'acct', 'held', 'verified', 'delete', 'share']

IGNORE_EXTENSIONS_RE = [r'.*.mht', r'.*.csv']

'''
    Parser class definition.

        Parameters:
            data_path (str):        Path to data which should be parsed (copies directory created by extractor)
            timeout (int):          Time limit in seconds for parsing a file.
            checkpoint (bool):      Determine whether to continue from the last checkpoint or start the
                                    entire parsing process again from the start.
            checkpoint_path (str):  Path to checkpoint file (default: parsed.json in the root directory)
'''
class DataParser():
    def __init__(self, data_path, timeout=10, checkpoint=False, checkpoint_path=None) -> None:
        self.format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=self.format, level=logging.INFO, datefmt="%H:%M:%S")
        self.data_path = Path(data_path)
        self.sites = os.listdir(self.data_path)
        self.timeout = timeout
        self.checkpoint_path = checkpoint_path
        self.parsed_data = {
            "addresses": {},
            "count": 0,
            "parsed_sites": {site: False for site in self.sites}
        }
        if checkpoint: self.load_checkpoint(checkpoint_path)

        # setup lemmatizer, download all required corpuses
        self.wnl = WordNetLemmatizer()
        nltk.download('punkt')
        nltk.download('words')
        nltk.download('wordnet')
        nltk.download('omw-1.4')
    
    def print_parsed_data(self):
        logging.info("Found these addresses: ")
        for key in self.parsed_data['addresses'].keys():
            users = []
            for record_key in self.parsed_data['addresses'][key]["records"].keys():
                users.append(self.parsed_data['addresses'][key]["records"][record_key]["owner"])
            record = f"{key} owner: {set(users)}"
            logging.info(record)

    def run(self):
        for site in self.sites:
            # checkpoint was loaded and site was already parsed
            if self.parsed_data['parsed_sites'][site]: continue

            logging.info(f"Parsing site: {site}")
            for root, _, files in os.walk(Path(self.data_path, site)):
                logging.info(f"Parsing {root}")
                for file in files:
                    if file == "something.nothing": continue
                    if any(re.match(regex, file) for regex in IGNORE_EXTENSIONS_RE): continue
                    path = Path(root, file)
                    self.parse_file(site, path)
            self.parsed_data["parsed_sites"][site] = True
            self.save_checkpoint(self.checkpoint_path)
        
        self.print_parsed_data()

    def save_checkpoint(self, path=None):
        logging.info(f"Saving checkpoint...")
        with open('parsed.json' if not path else path, 'w+') as fd:
            json.dump(self.parsed_data, fd, indent=4)
    
    def load_checkpoint(self, path=None):
        logging.info(f"Loading checkpoint...")
        with open('parsed.json' if not path else path, 'r') as fd:
            self.parsed_data = json.load(fd)    

    '''
        Parse given file with Beautiful Soup library.
        If parsing takes longer than given timeout limit, interrupt parsing. 
    '''
    def parse_file(self, site, file_path: Path):
        with open(file_path) as fd:
            try:
                contents = fd.read()
                soup = BeautifulSoup(contents, features="html.parser")
                with time_limit(self.timeout):
                    contexts = soup.find_all(text=PURE_ADDR_RE)
                    for context in contexts:
                        address = re.search(PURE_ADDR_RE, context).group(0)
                        currency = self.get_address_network(address)
                        title = soup.title.text if soup.title else "none"
                        owner = self.get_owner(soup)
                        self.create_data_object(site, file_path, address, context, currency, title=title if title else "unknown", owner=owner)

            except TimeoutException as e:
                logging.info(f"Processing of {file_path} has timed out!")

            except Exception as e:
                logging.info(f"{e}")

    '''
        Retrieve name of network(s) to which given address belongs.
    '''
    def get_address_network(self, address):
        networks = []
        for i, net_re in enumerate(ADDRESSES_RE):
            if re.match(net_re, address):
                networks.append(ADDRESSES_ENUM[i])
        return networks
    
    '''
        Try to find any data which could give a hint about user's context.
        Returns list of possible usernames or "unknown" if no candidates were found.
    '''
    def get_owner(self, soup: BeautifulSoup):
        users = []
        users_attributes = soup.find_all(attrs=USERS_RE)
        users_text = soup.find_all(text=USERS_RE)

        if users_attributes:
            for attribute in users_attributes:
                # tokenize text, remove anny punctation
                tokens = list(filter(lambda token: token not in string.punctuation, word_tokenize(attribute.text)))
                # lemmatize token and exclude any standard english words
                candidates = list(filter(lambda token: self.wnl.lemmatize(token.lower()) not in words.words() and re.match(r'^[A-Za-z][A-Za-z0-9_]+$', token), tokens))
                # exclude some more specific words not included in WorldNet corpus
                candidates = list(filter(lambda token: self.wnl.lemmatize(token.lower()) not in EXCLUDE_WORDS and not token.isupper(), candidates))   
                users.extend(candidates)

        if users_text:
            for text in users_text:
                tokens = list(filter(lambda token: token not in string.punctuation, word_tokenize(text)))
                candidates = list(filter(lambda token: self.wnl.lemmatize(token.lower()) not in words.words() and re.match(r'^[A-Za-z][A-Za-z0-9_]+$', token), tokens))
                candidates = list(filter(lambda token: self.wnl.lemmatize(token.lower()) not in EXCLUDE_WORDS and not token.isupper(), candidates))   
                users.extend(candidates)

        if len(users) == 0: return ["unknown"]
        users_set = set(users)
        users = list(users_set)
        return users

    '''
        Create new record object and append it into the self.parsed_data structure.
    '''
    def create_data_object(self, site, file_path: Path, address, context, currency, owner="unknown", title="unknown"):
        clean_file_path = Path(*file_path.parts[2:])
        record = {
            "owner": ','.join(owner),
            "site":  site,
            "title": title,
            "context": context,
        }
        record_hash = hashlib.md5(json.dumps(record).encode('utf-8')).hexdigest()
        record.update({"file_path": str(clean_file_path)})

        # address was alredy discovered
        if self.parsed_data['addresses'].get(address):
            # current record was already added
            if self.parsed_data['addresses'][address]['records'].get(record_hash): return
            self.parsed_data['addresses'][address]['records'].update({record_hash: record})
        
        else:
            data_object = {
                address: {
                    "records": {
                        record_hash: record
                    },
                    "currency": currency
                }
            }
            self.parsed_data['addresses'].update(data_object)
            self.parsed_data['count'] += 1

        users = []
        for record_key in self.parsed_data['addresses'][address]['records'].keys():
            users.extend(self.parsed_data['addresses'][address]['records'][record_key]['owner'].split(','))
            
        rc = f"{address} owner: {set(users)}, count: {self.parsed_data['count']}"
        logging.info(rc)


if __name__ == "__main__":
    parser = DataParser("data/copies", timeout=20, checkpoint=True)
    parser.run()
