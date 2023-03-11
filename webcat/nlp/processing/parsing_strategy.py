import abc
from bs4 import BeautifulSoup
import re
import json
import os

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

    def process_text(self, text):
        """Process the given text.
        """

        # Remove all the newlines
        text = text.replace("\n", " ")

        # Remove all the tabs
        text = text.replace("\t", " ")

        # Remove all the multiple spaces
        text = re.sub(" +", " ", text)

        # Remove all the leading and trailing spaces
        text = text.strip()

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

        return text

class HighestChildrenFrequencyStrategy(ParsingStrategy):
    """
        Parsing strategy which uses the tag with the most child nodes as the main content
        to split the web page into meaningful parts.
    """
    def __init__(self) -> None:
        super().__init__()

    def parse(self, content):
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
        
        texts = []
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
            text = self.process_text(child.text)
            if isinstance(text, list):
                texts.extend(text)
            else:
                texts.append(text)

        return texts
    
class StoredTemplatesStrategy(ParsingStrategy):
    """
        Parsing strategy which uses stored templates to split the web page into meaningful parts.
    """
    def __init__(self, templates_path="webcat/api/storage/templates.json") -> None:
        super().__init__()
        self.templates_path = templates_path
        self.root_path = os.path.dirname(os.path.abspath(__file__)) + "/../../../"
        # load templates
        with open(self.root_path + self.templates_path, "r") as f:
            self.stored_templates = json.load(f)
        
        # compile templates
        self.compile_templates()

    def compile_templates(self):
        # compile templates
        templates = {}
        for segment in self.stored_templates.keys():
            templates[segment] = {}
            for template in self.stored_templates[segment]:
                tag = template['tag']
                if tag not in templates[segment].keys():
                    templates[segment][tag] = {'classes': []}
                classes = templates[segment][tag]['classes']
                classes.extend(template['classes'])
                templates[segment][tag]['classes'] = classes
                templates[segment][tag]['classes_re'] = re.compile(r'(^|\s)(?:' + '|'.join(classes) + r')(\s|$)')
        
        self.templates = templates
        # create sets of classes
        for segment in self.templates.keys():
            for tag in self.templates[segment].keys():
                self.templates[segment][tag]['classes'] = list(set(self.templates[segment][tag]['classes']))

    def match_segments(self, soup):
        segments = {k: None for k in self.templates.keys()}
        for segment in self.templates.keys():
            for tag in self.templates[segment].keys():
                elements = soup.find_all(tag, class_=self.templates[segment][tag]['classes_re'])
                if len(elements) > 0:
                    segments[segment] = elements
                    break

        return segments

    def parse(self, content):
        soup = BeautifulSoup(content, features="html.parser")

        # match segments
        segments = self.match_segments(soup)

        # Find all the tags in the Beautiful Soup object
        if segments['post-body'] is not None:
            content_elements = segments['post-body']
        
        texts = []
        for el in content_elements:
            text = self.process_text(el.text)
            if isinstance(text, list):
                texts.extend(text)
            else:
                texts.append(text)
    
        return texts

if __name__ == "__main__":
    strategy = StoredTemplatesStrategy()
    print(strategy.parse(
        """
        <html>
            <body>
                <div>
                    <p>hello world</p>
                </div>
                <div class="post">
                    <p>hello world</p>
                    <div class="post-content">
                        <p>content</p>
                        <li class="username">
                            <p>author</p>
                        </li>
                        <p>content</p>
                    </div>
                </div>
            </body>
        </html>
        """
        ))