import abc
import re
import nltk
import urlextract
import datefinder

nltk.download('punkt')

# url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
url_regex = re.compile(r'((?:https?://|ftp://|http://|www\d{0,3}\.)'
                       r'(?:[^\s/$.?#][^\s]*)?)')
email_pattern = r'[\w\.-]+@[\w\.-]+'
datetime_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
html_pattern = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

class ParsingStrategy(object):
    """
        Abstract class for parsing strategies.
        The goal of the parsing strategy is to parse the given content and segment web pages into
        meaningful parts. The most interesting parts are the text parts grouped into posts, comments and
        other parts, which can occur on web forums.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parse(self, content):
        """Parse the given content.

        :param content: The content to parse.
        :type content: str
        :return: The parsed content.
        :rtype: str
        """
        pass
    
    @staticmethod
    def process_text(text):
        """Process the given text.
        """
        # Extract URLs and replace them with a placeholder [URL]
        # urls = urlextract.URLExtract().find_urls(text)
        # for url in urls:
        #     text = text.replace(url, "{{URL}}")

        # Remove all the newlines
        text = text.replace("\n", " ")

        # Remove all the tabs
        text = text.replace("\t", " ")

        # Remove all the multiple spaces
        text = re.sub(" +", " ", text)

        # Remove all the leading and trailing spaces
        text = text.strip()

        if text == "":
            return None
        
        # tokenize the text into sentences
        sentences = nltk.sent_tokenize(text)

        # initialize variables
        current_block = ""
        current_word_count = 0
        blocks = []

        for sentence in sentences:
            words = sentence.split()
            num_words = len(words)

            if current_word_count + num_words > 256:
                # if adding the current sentence will exceed the 256-word limit,
                # add the current block to the list of blocks and start a new block
                blocks.append(" " + current_block.strip() + " ")
                current_block = ""
                current_word_count = 0

            current_block += sentence + " "
            current_word_count += num_words

        # add the last block to the list of blocks
        if current_block.strip() != "":
            blocks.append(" " + current_block.strip())

        return blocks

    @staticmethod
    def clear_text(text:str, remove_urls=True, remove_emails=True, remove_html_tags=True, remove_datetime=True):
        text = text.replace("\n", " ")
        # Remove all the tabs
        text = text.replace("\t", " ")
        # Remove all the multiple spaces
        text = re.sub(" +", " ", text)
        # Remove all the leading and trailing spaces

        text = text.strip()
        if remove_html_tags:
            text = html_pattern.sub(' ', text)
        
        # remove urls
        # urls = re.findall(url_pattern, text)
        if remove_urls:
            urls = url_regex.findall(text)
            # urls = urlextract.URLExtract().find_urls(text)
            for url in urls:
                text = text.replace(url, " [URL] ")

        # remove emails
        # emails = re.findall(email_pattern, text)
        if remove_emails:
            text = re.sub(email_pattern, " [EMAIL] ", text)

        # remove datetime
        if remove_datetime:
            matches = datefinder.find_dates(text, source=True, strict=True)
            for match, match_text in matches:
                text = text.replace(str(match_text), " [DATETIME] ")

        return text
