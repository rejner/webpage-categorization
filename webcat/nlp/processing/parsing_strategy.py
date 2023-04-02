import abc
from collections import Counter
from bs4 import BeautifulSoup
import re
import json
import os
import nltk
import hashlib
import urlextract

nltk.download('punkt')

url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
email_pattern = r'[\w\.-]+@[\w\.-]+'

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
        # Extract URLs and replace them with a placeholder [URL]
        urls = urlextract.URLExtract().find_urls(text)
        for url in urls:
            text = text.replace(url, "{{URL}}")

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
                blocks.append(current_block.strip())
                current_block = ""
                current_word_count = 0

            current_block += sentence + " "
            current_word_count += num_words

        # add the last block to the list of blocks
        if current_block.strip() != "":
            blocks.append(current_block.strip())

        return blocks

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
            if text is None:
                continue

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
        hashes = []
        for el in content_elements:
            text = self.process_text(el.text)
            if text is None:
                continue
            texts.extend(text) if isinstance(text, list) else texts.append(text)
            hashes.append(hashlib.md5(text.encode('utf-8')).hexdigest())
    
        return texts, hashes

class TemplatesStrategy(ParsingStrategy):
    """
        Parsing strategy which uses stored templates from the database to split the web page into meaningful parts.
    """
    def __init__(self, templates) -> None:
        super().__init__()
        self.segment_types = ['post-body', 'post-header', 'post-author', 'post-area']
        # compile templates
        self.compiled_templates = self.compile_templates(templates)

    def _construct_regex(self, items):
        # colide lists of classes
        if len(items) > 0 and isinstance(items[0], list):
            items = list(set([item for sublist in items for item in sublist]))
        else:
            items = list(set(items))
        return re.compile(r'(^|\s)(?:' + '|'.join(items) + r')(\s|$)')
    
    def compile_templates(self, templates):
        compiled_templates = []
        for template in templates:
            t = {
                'id': template.id,
            }
            # compile segments
            # get all tags and classes for each segment type
            for type in self.segment_types:
                tags = [el.tag for el in template.elements if el.type == type]
                classes = [el.classes for el in template.elements if el.type == type]
                if len(tags) == 0:
                    t[type] = None
                    continue

                t[type] = {
                    'tags': tags,
                    'tags_re': self._construct_regex(tags),
                    'classes': classes,
                    'classes_re': self._construct_regex(classes)
                }
            compiled_templates.append(t)
        return compiled_templates

    def match_segments(self, soup):
        # iterate over segment types and find the first one that matches
        # the primary template is the post-area, if none of the templates match, return None
        segments = {k: None for k in self.segment_types}
        candidate_templates = []
        for template in self.compiled_templates:
            area = template['post-area']
            elements = soup.find_all(area['tags_re'], class_=area['classes_re'])
            if len(elements) > 0:
                #segments['post-area'] = elements
                #matched_template = template
                candidate_templates.append(template)
                # break
        
        if len(candidate_templates) == 0:
            return None
        
        # if there are multiple candidates, choose the one with the most matches
        for candidate_template in candidate_templates:
            # find the rest of the segments
            for segment in self.segment_types:
                template = candidate_template[segment]
                if template is None:
                    continue

                elements = soup.find_all(template['tags_re'], class_=template['classes_re'])
                if len(elements) > 0:
                    segments[segment] = elements

                if candidate_template[segment] is not None and segments[segment] is None:
                    # template does not match (not enough elements), try the next one
                    segments = {k: None for k in self.segment_types}
                    break
        
        if segments['post-area'] is None:
            return None
        
        return segments

    def parse(self, content):
        soup = BeautifulSoup(content, features="html.parser")
        # if content is not parsable return None

        # match segments
        segments = self.match_segments(soup)

        # Find all the tags in the Beautiful Soup object
        if segments is None:
            return None
        
        texts = []
        hashes = []
        content_elements = segments['post-body']
        for el in content_elements:
            text = self.process_text(el.text)
            if text is None:
                continue
            if isinstance(text, list):
                texts.extend(text) 
                hashes.extend([hashlib.md5(t.encode('utf-8')).hexdigest() for t in text])
            else:
                texts.append(text)
                hashes.append(hashlib.md5(text.encode('utf-8')).hexdigest())

        assert len(texts) == len(hashes)
                
        return texts, hashes

class PureRegexStrategy(ParsingStrategy):
    """
        Parsing strategy which uses regexes to split the web page into meaningful parts.
    """
    def __init__(self) -> None:
        super().__init__()
        self.header_patterns = [
            
            re.compile(r'(?<=Posted by ).+?(?=\n)'),
            re.compile(r'(?<=Posted on ).+?(?=\n)'),
            re.compile(r'(?<=Reply by ).+?(?= \n)'),
            re.compile(r'(?<=Reply on ).+?(?= \n)'),
            # date and time
            re.compile(r'\d{1,2} \w{3} \d{4} \d{1,2}:\d{2} [AP]M')
        ]
        self.content_patterns = [
            re.compile(r'(?<=\n\n).+?(?=\n\n)'),
            re.compile(r'(?<=wrote: ).+?(?=\n)'),
        ]    
        # compile templates

    

    def parse(self, content):
        soup = BeautifulSoup(content, features="html.parser")
        # if content is not parsable return None
        texts = soup.text
        # print(texts)
        # extract patterns
        headers = []
        contents = []
        for pattern in self.header_patterns:
            headers.extend(re.findall(pattern, texts))
        for pattern in self.content_patterns:
            contents.extend(re.findall(pattern, texts))
        # split into segments
        texts = texts.split('\n')
        texts = [t for t in texts if len(t) > 0]
        hashes = [hashlib.md5(t.encode('utf-8')).hexdigest() for t in texts]
        return texts, hashes
        # match segments
        segments = None

        # Find all the tags in the Beautiful Soup object
        if segments is None:
            return None
        
        texts = []
        hashes = []
        content_elements = segments['post-body']
        for el in content_elements:
            text = self.process_text(el.text)
            if text is None:
                continue
            if isinstance(text, list):
                texts.extend(text) 
                hashes.extend([hashlib.md5(t.encode('utf-8')).hexdigest() for t in text])
            else:
                texts.append(text)
                hashes.append(hashlib.md5(text.encode('utf-8')).hexdigest())

        assert len(texts) == len(hashes)
                
        return texts, hashes

class TemplatesStrategy_v2(ParsingStrategy):
    """
        Parsing strategy which uses regexes to split the web page into meaningful parts.
        V2 Teplates look like this:
            {   [
                {
                    "tag": "div",
                    "parent-tag": "div",
                    "grandparent-tag": "div",
                    "depth": 3,
                    "type": "post-header"
                },
                {
                    "tag": "em",
                    "parent-tag": "div",
                    "grandparent-tag": "div",
                    "depth": 3,
                    "type": "post-author"
                }
                ...
                ]
           }
    """
    def __init__(self, templates) -> None:
        super().__init__()
        self.segment_types = ['post-message', 'post-header', 'post-author']
        self.ids_to_types = {k+1: v for k, v in enumerate(self.segment_types)}
        self.templates = templates

    def calculate_element_depth(self, element):
        """
            Calculates the depth of the element.
        """
        depth = 0
        while element.parent:
            depth += 1
            element = element.parent
        return depth
    
    def match_segments(self, soup):
        # iterate over segment types and find the first one that matches
        # the primary template is the post-area, if none of the templates match, return None
        segments = {k: None for k in self.segment_types}
        for template in self.templates:
            tmp_segments = {k: None for k in self.segment_types}
            segments_match = True
            for template_element in template['elements']:
                segment = self.ids_to_types[template_element['type_id']]
                elements = soup.findAll(template_element['tag'])
                if elements is None:
                    segments_match = False
                    break # template does not match

                # filter elements by parent tag
                elements = list(filter(lambda x: x.parent.name == template_element['parent_tag'], elements))
                if len(elements) == 0:
                    segments_match = False
                    break

                # filter elements by grandparent tag
                elements = list(filter(lambda x: x.parent.parent.name == template_element['grandparent_tag'], elements))
                if len(elements) == 0:
                    segments_match = False
                    break

                # filter elements by depth
                elements = list(filter(lambda x: self.calculate_element_depth(x) == template_element['depth'], elements))
                if len(elements) == 0:
                    segments_match = False
                    break
                
                # all elements must have the same next element tag
                # some elements may not have a next element, but keep track of nones
                elements_next_type = ['string' if isinstance(e.next, str) else 'element' for e in elements]
                next_element_counts = Counter(elements_next_type)
                # count the number of each next element
                
                # get the most common next element
                most_common_next_element = next_element_counts.most_common(1)[0][0]
                elements = [e for e, t in zip(elements, elements_next_type) if t == most_common_next_element]
                # filter elements by most common next element
                # elements = list(filter(lambda x: x.next.tag == most_common_next_element.tag, elements))
                if len(elements) == 0:
                    segments_match = False
                    break

                
                tmp_segments[segment] = elements
                
            if segments_match:
                segments = tmp_segments
                break
        
        return segments

    # def clear_text(self, text):
    #     """
    #         Removes all the newlines from the text.
    #     """
    #     # Remove all the newlines
    #     text = text.replace("\n", " ")
    #     # Remove all the tabs
    #     text = text.replace("\t", " ")
    #     # Remove all the multiple spaces
    #     text = re.sub(" +", " ", text)
    #     # Remove all the leading and trailing spaces
    #     text = text.strip()
    #     return text
    
    def clear_text(self, text):
        text = text.replace("\n", " ")
        # Remove all the tabs
        text = text.replace("\t", " ")
        # Remove all the multiple spaces
        text = re.sub(" +", " ", text)
        # Remove all the leading and trailing spaces
        text = text.strip()
        # remove urls
        # urls = re.findall(url_pattern, text)
        text = re.sub(url_pattern, ' {{URL}} ', text)
        # remove emails
        # emails = re.findall(email_pattern, text)
        text = re.sub(email_pattern, " {{EMAIL}} ", text)
        # remove html tags
        text = re.sub(r'<[^>]*>', '', text)
        return text
    
    def parse(self, content):
        soup = BeautifulSoup(content, features="html.parser")
        # if content is not parsable return None

        # match segments
        segments = self.match_segments(soup)

        # Find all the tags in the Beautiful Soup object
        if segments is None:
            return None
        
        message_elements = segments['post-message']
        author_elements = segments['post-author']
        header_elements = segments['post-header']
        MD_text = ""
        content_objects = []

        content_len = max(len(message_elements), len(author_elements), len(header_elements))
        for elements in [message_elements, author_elements, header_elements]:
            # length of all elements must be the same, or 0 (if no elements were found)
            assert len(elements) == content_len or len(elements) == 0

        for m_el, a_el, h_el in zip(message_elements, author_elements, header_elements):
            # messages can be split because they contain too much text
            m_text = self.process_text(m_el.text)
            # only clear authors and headers, because they will not be analyzed by the model
            a_text = self.clear_text(a_el.text)
            h_text = self.clear_text(h_el.text)
      
            MD_text = ""
            MD_text += "## " + h_text + "\n"
            MD_text += "### " + a_text + "\n"
            if isinstance(m_text, list):
                for t in  m_text:
                    MD_text += t + "\n"
            else:
                MD_text += m_text + "\n"

            hsh = hashlib.md5(MD_text.encode('utf-8')).hexdigest()
            # TODO: author and header swapped, this seem to be rooted in the templates
            # For now, it is ok, but it should be fixed
            content_objects.append({
                "message": m_text,
                "author": h_text,
                "header": a_text,
                "hash": hsh,
            })

        return content_objects


if __name__ == "__main__":
    strategy = TemplatesStrategy_v2(
        [
        {   "creation_date": "2014-11-05",
            "origin_file": "viewtopic.php_pid=4282",
            "elements": [
            {
                "tag": 'a', "parent_tag": 'em', "grandparent_tag": 'span', "depth": 12, "type": "post-author"
            },
            {
                "tag": 'h4', "parent_tag": 'div', "grandparent_tag": 'div', "depth": 10, "type": "post-header"
            },
            {
                "tag": 'div', "parent_tag": 'div', "grandparent_tag": 'div', "depth": 10, "type": "post-message"
            }
            ]
        },
        ],
    
    )
    # load file
    with open("/workspaces/webpage_categorization/data/bungee54-forums/bungee54-forums/2014-11-05/viewtopic.php_pid=4282", "r") as f:
        content = f.read()
    
    output = strategy.parse(content)
    if output:
        for o in output:
            print("----------------")
            print(o)
            print("----------------")