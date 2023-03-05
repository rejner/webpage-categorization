import abc
from bs4 import BeautifulSoup
import re

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

class HighestChildrenFrequencyStrategy(ParsingStrategy):
    """
        Parsing strategy which uses the tag with the most child nodes as the main content
        to split the web page into meaningful parts.
    """
    def __init__(self) -> None:
        super().__init__()

    def parse(self, content):
        texts = []
        soup = BeautifulSoup(content, features="html.parser")

        # get rid of scirpt/style and table tags
        for unnecessary in soup(["script", "style", "nav", "table", "header"]):
            unnecessary.extract()
    
        # Find all the tags in the Beautiful Soup object
        tags = soup.find_all()

        # Initialize a variable to keep track of the tag with the most children
        most_children = None
        max_children = 0

        # Iterate over all the tags
        for tag in tags:
            # Count the number of children of the current tag
            num_children = len(list(tag.children))
        
            # If the current tag has more children than the current maximum, update the maximum
            if num_children > max_children:
                max_children = num_children
                most_children = tag
        
        for child in most_children.children:
            if not child.name: # ignore comments
                continue
            # remove all children with class button in it
            # get all children with class button
            buttons = child.find_all(class_=re.compile
            ("button"))
            # remove all children with class button
            for button in buttons:
                button.decompose()

            # get text from the tag
            text = child.text
            # strip the text
            text = text.strip()
            # remove newlines
            text = text.replace("\n", " ")
            # remove multiple spaces
            text = " ".join(text.split())
            if text != "":
                # count word count in tex
                word_count = len(text.split())
                # if word count is more than 256, then split the text into 256 words,
                # split text into multiple 256 blocks
                if word_count > 256:
                    # split text into 256 words
                    text = text.split()
                    # split text into 256 words
                    text = [text[i:i+256] for i in range(0, len(text), 256)]
                    # join the text
                    text = [" ".join(t) for t in text]

                if isinstance(text, list):
                    texts.extend(text)
                else:
                    texts.append(text)

        return texts