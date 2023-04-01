from collections import Counter
import os
import openai
import json
import bs4
from .base import TemplateEngine
from .exceptions import MissingOpenAIKeyError
import re

class ChatGPTTemplateEngine(TemplateEngine):
    """
        Uses OpenAI's ChatGPT API to generate templates from a given file.

        The website is pre-processed using the following steps:
        1. Extract all text from the website (using BeautifulSoup)
        2. Each line of text is cut to a maximum length of MAX_LINE_LENGTH
         - The hypothesis is that the headers are usually short and the message is usually long, but
           to capture context for segmentation, we don't need full messages.
        3. The text is cut to a maximum length of MAX_INPUT_LENGTH (due to API limitations)
         - This is also fine, because it is sufficient to capture just a few posts.
        4. The text is sent to the OpenAI API and parsed by ChatGPT model.
         - The model is instructed to output a JSON array with the found segments "post-header", "post-author" and "post-message".
        5. The JSON array is parsed and the segments are extracted.
        6. The segments are grouped by type and the most common segment is selected as the template.
         - For each identified segment, candidate elements are extracted based on text content of the segment
           parsed by the model.
         - The most common and repeated element is selected as the template for each segment.
            - The candidate element must be present in all indentified segments of the same type.
            - IE: If the model identified 3 segments of type "post-header", the template must be present in all 3 segments.
         - We store node tag, its parent tag and its parent's parent tag as the template, together
           with the node depth. These information are sufficient to identify the node in the HTML. 
        7. The template is returned.

        Example output of the model (3 posts/segments):
        [
            {
                "post-header": "Who´s running this?",
                "post-author": "ScReaper",
                "post-message": "Step up, declare your role.The darkmarkets is bleeding and there´s no trust left... why should i sell my shit on your market and how can you guarantee you wont run with the wallets?"
            },
            {
                "post-header": "Who´s running this?",
                "post-author": "brickmaster",
                "post-message": "Good Point, I'd like to hear a response to that question. I'm feeling kind of iffy about selling on this site especially since there are little to no vendors and no sign of customers."
            },
            {
                "post-header": "Who´s running this?",
                "post-author": "J0K3R",
                "post-message": "ScReaper wrote:Step up, declare your role.The darkmarkets is bleeding and there´s no trust left... why should i sell my shit on your market and how can you guarantee you wont run with the wallets?I can't guarantee anything"
            }
        ]
    """
    def __init__(self) -> None:
        super().__init__()
        self.MAX_INPUT_LENGTH = 512
        self.MAX_LINE_LENGTH = 64
        self.START_OFFSET = 256
        # self.PROMPT_START = "Analyze the text I give you and output only a JSON array with the found segments \"post-header\", \"post-author\" and \"post-message\". I need you to segment this raw text extracted from HTML of a forum. Each newline character delimiters a logical section of a DOM tree. The value of the segment should be the exact matched text. Try to extract at least 3 posts. The input is:\n\n"
        self.PROMPT_START = "I want you to act as a data extraction tool and extract post titles, post authors, and post messages from raw text extracted from HTML code of a forum website. The raw text is separated by newline characters and the desired output is a JSON array of objects in the format [{\"post-title\": \"some title\", \"post-author\": \"some author\", \"post-message\": \"some message\"}]. Your task is to segment the raw text and extract the required information from each segment. Remember that each segment contains only one part of the required information. The input is:\n\n"
        self.SYSTEM_PROMPT = "You are a server for analyzing text data, responding in JSON array format according to instructions."
        self.segment_types = ["post-header", "post-author", "post-message"]
        self.most_likely_tags = {
            "post-header": ["h1", "h2", "h3", "h4", "h5", "h6", "div", "span"],
            "post-author": ["div", "a"],
            "post-message": ["div", "p"]
        }
        self.setKey()
    
    def setKey(self, key=None):
        if key is None:
            try:
                key = os.environ["OPENAI_API_KEY"]
            except KeyError:
                raise MissingOpenAIKeyError("OpenAI API key not provided.")
            
        self.api_key = key
        openai.api_key = self.api_key

    @property
    def name(self):
        return "ChatGPT Template Engine"
    
    @property
    def requiresKey(self):
        return True
    
    @property
    def description(self):
        return "Uses OpenAI's ChatGPT API to generate templates from a given file."

    def analyze_text(self, text):
        """
        Response format:
        {
            'id': 'chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve',
            'object': 'chat.completion',
            'created': 1677649420,
            'model': 'gpt-3.5-turbo',
            'usage': {'prompt_tokens': 56, 'completion_tokens': 31, 'total_tokens': 87},
            'choices': [
            {
                'message': {
                'role': 'assistant',
                'content': 'The 2020 World Series was played in Arlington, Texas at the Globe Life Field, which was the new home stadium for the Texas Rangers.'},
                'finish_reason': 'stop',
                'index': 0
            }
            ]
        }
        
        """
        print("Analyzing text...")
        prompt = self.PROMPT_START + text
        payload = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # response = RESPONSE_TOTRUGA_2
        # response = RESPONSE
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=payload,
            temperature=0.1,
        )
        print("Response:")
        print("-"*100)
        print(response)
        print("-"*100)

        # load dictionary into object
        response = Struct(response)
        output = response.choices[0].message.content

        
        # output = "Here is the output in the required format:\n\n[{\"post-title\": \"Does anyone need samples? I'm an old vendor from S\", \"post-author\": \"SupremeSmoke\", \"post-message\": \"I used to be an avid member of Silk road 1 but after losing ever\"}]"
        output = self.verify_output(output)
        
        # return output
        return json.loads(output)

    def verify_output(self, output:str):
       
        # verfity that output starts and ends as JSON array should
        is_json_array = re.compile(r"(\[.*?\])", re.DOTALL)
        if not is_json_array.match(output):
            tmp_output = output
            if not tmp_output.startswith("["):
                # try to iterate from the start to reach '['
                for i in range(len(tmp_output)):
                    if tmp_output[i] == "[":
                        tmp_output = tmp_output[i:]
                        break

            if not tmp_output.endswith("]"):
                # try to iterate from the end to reach ']'
                for i in range(len(tmp_output)):
                    if tmp_output[-i] == "]":
                        tmp_output = tmp_output[:-(i-1)]
                        break
                
            tmp_output = tmp_output.strip()
            tmp_output = tmp_output.strip(".,;:!?")
            # now try to verify
            if is_json_array.match(tmp_output):
                output = tmp_output
                return output

            tmp_output = output
            # try to repair
            tmp_output =  tmp_output.strip()
            tmp_output =  tmp_output.strip(".,;:!?")

            # ensure that output ends with ], strip all other characters
            if not  tmp_output.endswith("]"):
                 tmp_output =  tmp_output + "]"

            # ensure that output starts with [
            if not  tmp_output.startswith("["):
                 tmp_output = "[" +  tmp_output

            if not is_json_array.match( tmp_output):
                raise ValueError("Output is not a valid JSON array, nor can it be repaired.")

            output =  tmp_output

        return output


    def parse_html(self, html_file):
        """
            Parses the HTML and returns text.
        """
        with  open(html_file, 'r') as f:
            html = f.read()
        soup = bs4.BeautifulSoup(html, "html.parser")
        # remove all scripts, head, style, meta, link, title, etc.
        for tag in soup.find_all(["script", "head", "style", "meta", "link", "title", "noscript", "iframe", "svg", "path", "img", "button", "input", "form", "footer", "header", "nav", "section"]):
            tag.decompose()

        text = soup.get_text()
        # split text into lines by newlines and tabs
        text = re.split(r"\n|\t", text)
        # keep at maximum one empty line between lines
        # simple automata
        last_line_empty = False
        for i in range(len(text)):
            if text[i] == " ":
                text[i] = ""
            if text[i] == "":
                if last_line_empty:
                    text[i] = None
                else:
                    last_line_empty = True
            else:
                last_line_empty = False
        text = [x for x in text if x is not None]

        # it helps to start at a later point in the text to eliminate navigation and other stuff
        if self.START_OFFSET > 0 and len(text)*2 > self.START_OFFSET:
            text = text[self.START_OFFSET:]

        # iterate through text and count the number of characters
        # if the number of characters exceeds the max input length, then cut the text
        for i in range(len(text)):
            if len(text[i]) > self.MAX_LINE_LENGTH:
                text[i] = text[i][:self.MAX_LINE_LENGTH]
        
        # join text back together
        text = "\n".join(text)
        if len(text) > self.MAX_INPUT_LENGTH:
            text = text[:self.MAX_INPUT_LENGTH]
        return text, soup
        
    def calculate_element_depth(self, element):
        """
            Calculates the depth of the element.
        """
        depth = 0
        while element.parent:
            depth += 1
            element = element.parent
        return depth

    def analyze_segments(self, segments, soup: bs4.BeautifulSoup):
        if segments is None:
            return None
        
        # iterate through the segments and find the corresponding HTML elements
        # for each segment, find the corresponding HTML elements
        candidate_elements = {k: [] for k in self.segment_types}
        for segment_type in self.segment_types:
            for segment in segments:
                if segment_type in segment:
                    text_to_find = segment[segment_type]
                    text_to_find = text_to_find.split("\n")[0]
                    if text_to_find == "":
                        continue
                    
                    # split text into tri-grams and find the corresponding HTML elements
                    text_to_find = text_to_find.split(" ")
                    # if the number of words is even, then use bi-grams, otherwise use tri-grams
                    N_GRAM_SIZE = 2 if len(text_to_find) % 2 == 0 else 3
                    text_to_find = [text_to_find[i:i+N_GRAM_SIZE] for i in range(0, len(text_to_find), N_GRAM_SIZE)]
                    text_to_find = [" ".join(x) for x in text_to_find]
                    text_to_find = "|".join(text_to_find)
                    # compile regex pattern for tri-grams
                    pattern = re.compile(text_to_find)
                    elements = [el.parent for el in soup.findAll(text=pattern)]
                    # elements = [el for el in elements if re.match(pattern, el.get_text())]
                    if elements:
                        candidate_elements[segment_type].append(elements)
        
        # construct a list of candidate elements for each segment from special objects
        candidates = {k: [] for k in self.segment_types}
        for type, elements in candidate_elements.items():
            for els in elements:
                tmp = []
                for el in els:
                    try:
                        tmp.append(
                            TemplateElements(
                                tag=el.name,
                                parent_tag=el.parent.name,
                                grandparent_tag=el.parent.parent.name,
                                depth=self.calculate_element_depth(el),
                            )
                        )
                    except Exception as e:
                        print(e)
                candidates[type].append(tmp)

        # count the number of occurences of each element
        candidate_counts = {k: [] for k in self.segment_types}
        for type, els in candidates.items():
            for el in els:
                candidate_counts[type].append(Counter(el))
                
        # get intersection of all candidate elements from each segment
        # (if there are multiple segments for a given type, the candidate elements must be in all segments)
        filtered_candidates = {k: [] for k in self.segment_types}
        for type, els in candidates.items():
            if len(els) > 0:
                filtered_candidates[type] = list(set.intersection(*map(set, els)))
            else:
                filtered_candidates[type] = []

        # if some of the segments have more than one candidate element, then we need to filter them
        # take the most common element
        for type, els in filtered_candidates.items():
            if len(els) > 1:
                # for each element, count the number of occurences in the candidate_counts
                # take the most common
                counts = {}
                for el in els:
                    counts[el] = 0
                    for cnt in candidate_counts[type]:
                        if el in cnt:
                            counts[el] += cnt[el]

                # candidate element is the one with the most occurences
                filtered_candidates[type] = max(counts, key=lambda x: counts[x])
            
            # if there is only one candidate element, then we can just take it
            if len(els) == 1:
                filtered_candidates[type] = els[0]

            if len(els) == 0:
                filtered_candidates[type] = None

        return filtered_candidates
    
    def determine_template_elements(self, candidates, soup: bs4.BeautifulSoup):
        """
            Determines the template elements from the candidates.
        """
        elements = {k: [] for k in self.segment_types}
        for type, el in candidates.items():
            if el is None:
                continue
            tag = el.tag
            parent_tag = el.parent_tag
            grandparent_tag = el.grandparent_tag
            depth = el.depth

            # check if parent has multiple same elements of the current element
            # if it does, then our template element is the parent (can be the case of multiple paragraphs)
            parent_els = soup.findAll(parent_tag)
            parent_els = [el for el in parent_els if el.parent.name == grandparent_tag and self.calculate_element_depth(el) == depth - 1]
            el_replaced = False
            for parent_el in parent_els:
                same_children_cnt = 0
                for child in parent_el.children:
                    if child.name == tag and parent_el.parent.name == grandparent_tag:
                        same_children_cnt += 1

                # if there are multiple same children, then the parent is the template element
                if same_children_cnt > 1:
                    tag = parent_tag
                    parent_tag = parent_el.parent.name
                    grandparent_tag = parent_el.parent.parent.name
                    depth = depth - 1
                    el_replaced = True
                    break

            # find all elements that match the template element
            els = soup.findAll(tag)
            if not el_replaced:
                els = [el for el in els if el.parent.name == parent_tag and el.parent.parent.name == grandparent_tag and self.calculate_element_depth(el) == depth and el.next != "\n"]
            else:
                els = [el for el in els if el.parent.name == parent_tag and el.parent.parent.name == grandparent_tag and self.calculate_element_depth(el) == depth]
            elements[type] = els
        
        return elements
    
    def template_from_file(self, file_path):
        """
            Generates a template from a given file.
        """
        text, soup = self.parse_html(file_path)
        segments = self.analyze_text(text)
        # replace keys "post-title" with "post-header"
        segments = [{k.replace("post-title", "post-header"): v for k, v in segment.items()} for segment in segments]
        candidates = self.analyze_segments(segments, soup)
        elements = self.determine_template_elements(candidates, soup)

        for type, el in elements.items():
            if len(el) == 0:
                print("No element found for type", type)
            if len(el) > 1:
                print("Multiple elements found for type", type)

        # if all segments have the same amount of elements, then we can use the first element
        # we found a perfect template
        perfect_match = False
        if all(len(el) == len(elements[self.segment_types[0]]) for el in elements.values()):
            perfect_match = True

        presumed_header = False
        if not perfect_match:
            # headers can often be screwed, because messages can be just reactions
            if len(elements["post-message"]) == len(elements["post-author"]):
                # presume that the longest element is the header common to all messages
                longest_el = max(elements["post-header"], key=lambda x: len(x.text))
                elements["post-header"] = [longest_el for _ in range(len(elements["post-message"]))]
                presumed_header = True


        template_proposal = {}
        # template = {}
        contents = {k: [el.text for el in v] for k, v in elements.items()}
        # if we presumed the header, then append (presumed) to the header
        if presumed_header:
            contents["post-header"] = [el + " (presumed)" for el in contents["post-header"]]

        obj_elements = []
        for type, els in elements.items():
            if len(els) == 0:
                # template[type] = None
                contents[type] = []
            else:
                element = TemplateElements(
                    tag=els[0].name,
                    parent_tag=els[0].parent.name,
                    grandparent_tag=els[0].parent.parent.name,
                    depth=self.calculate_element_depth(els[0]),
                ).__dict__
                element["type"] = type
                obj_elements.append(element)

        template_proposal["perfect_match"] = perfect_match
        template_proposal["contents"] = contents
        template_proposal["elements"] = obj_elements
        return template_proposal

    def pretty_print(self, template):
        """
            Pretty prints the template.
        """
        for type, els in template.items():
            print(f"Type: {type}, Elements: {len(els)}")
            for el in els:
                # print max 100 characters
                print(el.text[:100])
            print()

class TemplateElements():
    def __init__(self, tag, parent_tag, grandparent_tag, depth):
        self.tag = tag
        self.parent_tag = parent_tag
        self.grandparent_tag = grandparent_tag
        self.depth = depth
    
    def __eq__(self, other):
        # classes might not be so important
        return self.tag == other.tag and self.parent_tag == other.parent_tag and self.grandparent_tag == other.grandparent_tag, self.depth == other.depth

    def __hash__(self):
        return hash((self.tag, self.parent_tag, self.grandparent_tag, self.depth))
    
    # make TemplateElements json serializable
    def __repr__(self):
        return str(self.__dict__)
    
    def __str__(self):
        return str(self.__dict__)    



class Struct(object):
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value

RESPONSE = {
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "[\n  {\n    \"post-header\": \"Topic: Bungee54 State of Operations\",\n    \"post-author\": \"Calico Jack\",\n    \"post-message\": \"To all of our friends, valued customers, competitors, partners,  haters and trolls of Bungee54!Please read the following announcement carefully and in it's entirety:The Bungee54 Team is going through a transition that will involve us taking a step back int\\nBAFH\\\"Cryptography is Freedom\\\"\"\n  },\n  {\n    \"post-header\": \"Re: Bungee54 State of Operations\",\n    \"post-author\": \"Fahshizzle\",\n    \"post-message\": \"thanks for the heads up, certainly makes me feel better about all the FUD thats been going around.sounds like ill need start shopping around for a new vendor  if youre still willing to work with me PM please otherwise, do you have any suggestions for the c\"\n  },\n  {\n    \"post-header\": \"Re: Bungee54 State of Operations\",\n    \"post-author\": \"drmindbender\",\n    \"post-message\": \"Despite my latest package order not having arrived for more than 2 weeks... and I'm going to assume it was probably seized in the next day or 2, I am very happy to have read your State of Operations.\\u00a0 This goes very closely with how I personally feel suppl\"\n  }\n]",
        "role": "assistant"
      }
    }
  ],
  "created": 1680097471,
  "id": "chatcmpl-6zQOFctAOP8RQiAs9THN8sViZLFuF",
  "model": "gpt-3.5-turbo-0301",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 291,
    "prompt_tokens": 1224,
    "total_tokens": 1515
  }
}