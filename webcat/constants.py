import re

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

DEFAULT_CONFIG = {
    
}

dummy_corpus = [
    "I am selling a new strain of designer drugs that will blow your mind. If you want to try them out, send me a message and we can make a deal.",

    "I am looking for someone to help me launder money through a series of offshore accounts. If you have experience with this type of work, please contact me.",

    "I am selling stolen credit card numbers and other personal information. If you are interested, send me a message and we can discuss pricing.",

    "I am looking for someone to help me hack into a government website. If you have the skills and are interested in the job, please contact me.",

    "I am selling a collection of rare and valuable stolen artworks. If you are interested in purchasing any of these pieces, please send me a message.",

    "I am looking for someone to help me set up a new cryptocurrency exchange. If you have experience with this type of work, please contact me.",

    "I am selling a new type of malware that allows you to take control of any computer. If you are interested, please send me a message and we can discuss pricing.",

    "I am looking for someone to help me set up a new darknet market. If you have experience with this type of work, please contact me.",

    "I am selling a collection of stolen login credentials for various online accounts. If you are interested, please send me a message and we can discuss pricing.",

    "I am looking for someone to help me set up a new cryptocurrency wallet. If you have experience with this type of work, please contact me.",

    "I am accepting payments in Bitcoin at this address: 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2.",

    "If you want to purchase my stolen credit card numbers, please send the payment to this Ethereum address: 0x1234567890.",

    "I am accepting payments in Monero at this address: 4JUdGzvrMFDWrUUwY3toJATSeNwjn54LkCnKBPRzDuhzi5vSepHfUckJNxRL2gjkNrSqtCoRUrEDAgRwsQvVCjZbS4D4N1Q8FHXpEsBXzxZtZd.",

    "I am looking for a supplier who can provide me with high quality methamphetamine. I need to make a large order, so the supplier must be reliable and able to deliver on time. If you know anyone who can help me, please let me know.",

    "I am an experienced hacker looking for new challenges. I have experience in a variety of areas, including web exploitation, password cracking, and social engineering. If you have a target you would like me to take down, I would be happy to discuss it with you.",

    "Attention all users! We have recently discovered a new phishing scam targeting our customers. If you receive an email claiming to be from us asking for your login information, do not respond! This is a scam and the perpetrators are trying to steal your personal information. If you have already responded to one of these emails, please change your password immediately.",

    "I am selling high quality replicas of designer handbags. These bags are identical to the real thing and no one will be able to tell the difference. If you are interested, please send me a message and I will give you more information on pricing and availability.",

    "I am offering a new service that allows you to attack any website you choose. With this service, you will be able to take down any website and cause chaos on the internet. If you are interested in this service, please contact me for more information.",

    "I am selling Bitcoin at a discounted price. This is a limited time offer, so act fast if you want to take advantage of this deal. I accept a variety of cryptocurrencies, including Ethereum, Litecoin, and Monero. If you are interested, please send me a message and we can make a deal.",

    "Grizzly bears are dangerous animals.",
]