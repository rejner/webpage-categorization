from collections import Counter
import openai
import json
import bs4
from .base import TemplateEngine
import re
import logging
from webcat.models_extension import Element
from lxml import etree

class ChatGPTTemplateEngine_v2(TemplateEngine):
    """
        Uses OpenAI's ChatGPT API to generate templates from a given file.

        The website is pre-processed using the following steps:
        1. Extract all text from the website (using BeautifulSoup)
         - Keep the corresponding DOM node for each text line.
         - Must be done in a way that preserves the order of the text lines,
           maybe some kind of mapping between the text and the DOM node.
        2. Each line of text is cut to a maximum length of MAX_LINE_LENGTH
         - The hypothesis is that the headers are usually short and the message is usually long, but
           to capture context for segmentation, we don't need full messages.
        3. The text is cut to a maximum length of MAX_INPUT_LENGTH (due to API limitations)
         - This is also fine, because it is sufficient to capture just a few posts.
        4. The text is sent to the OpenAI API and parsed by ChatGPT model.
         - The model is instructed to output a JSON array with the found segments "post-header", "post-author" and "post-message".
        5. The JSON array is parsed and the content types are extracted.
        6. Find the DOM node that contains the text for each segment.
         - These are the template nodes.
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
        self.MAX_INPUT_LENGTH = 128
        self.MAX_LINE_LENGTH = 64
        self.START_OFFSET = 0
        # self.PROMPT_START = "Analyze the text I give you and output only a JSON array with the found segments \"post-header\", \"post-author\" and \"post-message\". I need you to segment this raw text extracted from HTML of a forum. Each newline character delimiters a logical section of a DOM tree. The value of the segment should be the exact matched text. Try to extract at least 3 posts. The input is:\n\n"
        self.PROMPT_START = "I want you to act as a data extraction tool and extract post titles, post authors, and post messages from raw text extracted from HTML code of a forum website. The raw text is separated by newline characters and the desired output is a JSON array of objects in the format [{\"post-title\": \"some title\", \"post-author\": \"some author\", \"post-message\": \"some message\"}]. Your task is to segment the raw text and extract the required information from each segment. Remember that each segment contains only one part of the required information. The input is:\n\n"
        self.SYSTEM_PROMPT = "You are a server for analyzing text data, responding in JSON array format according to instructions."
        self.segment_types = ["post-title", "post-author", "post-message"]
        self.most_likely_tags = {
            "post-title": ["h1", "h2", "h3", "h4", "h5", "h6", "div", "span"],
            "post-author": ["div", "a", "strong"],
            "post-message": ["div", "p"]
        }
    
    def setKey(self, key):
        self.api_key = key
        openai.api_key = self.api_key

    @property
    def name(self):
        return "ChatGPT Template Engine v2"
    
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
        logging.info("Analyzing text...")
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
        #OUTPUT_BUNGE = '[{"post-title": "Future of Bungee Shop and all Black market sites", "post-author": "Reximusmaximus", "post-message": "Just Curious. I am an avid Silk road supporter, but I strongly l"}, {"post-title": "Re: Future of Bungee Shop and all Black market sites", "post-author": "Mm31qIPrZ", "post-message": "I believe their current plan is to keep up their semi-private sh"}, {"post-title": "Re: Future of Bungee Shop and all Black market sites", "post-author": "Reximusmaximus", "post-message": "I mean ill probably make an account, but after the fall of SR 1."}]'
        # OUTPUT_UTOPIA = '[{"post-title": "Warning from DRP2 (Silk Road 2.0): Do not spam our forums!", "post-author": "SorryMario", "post-message": "BTW, 405 posts is nothing. frim could do that by his little auti\\nIt probably is him in all honesty haha! Congrats on Modship, jus"}, {"post-title": "Warning from DRP2 (Silk Road 2.0): Do not spam our forums!", "post-author": "ChingChingChingChing", "post-message": "Fuck SR2 and and admin there (that\'s you, scout, you little fuck\\nIf they \\"start returning fire\\" that\'s pretty much a declaration \\nI see this as desperation. Their own little scam of a marketplac\\nsticksNshits wrote:\\nI was unaware that DPR2 was even active at this point?\\nLol, the mods are spreading some bullshit that DPR2 has returned"}]'
        # return OUTPUT_UTOPIA, prompt, 0
        # response = RESPONSE_TOTRUGA_2
        # response = RESPONSE

        # OUTPUT_BUNGEE = '[{"post-title": "Future of Bungee Shop and all Black market sites", "post-author": "Reximusmaximus", "post-message": "Just Curious. I am an avid Silk road supporter, but I strongly l"}, {"post-title": "Future of Bungee Shop and all Black market sites", "post-author": "Mm31qIPrZ", "post-message": "I believe their current plan is to keep up their semi-private sh"}, {"post-title": "Future of Bungee Shop and all Black market sites", "post-author": "Reximusmaximus", "post-message": "I mean ill probably make an account, but after the fall of SR 1."}]'
        # return OUTPUT_BUNGEE, prompt, 0
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=payload,
                temperature=0.1,
            )
        except Exception as e:
            logging.error("Error in OpenAI API call:")
            logging.error(e)
            raise e
        
        logging.info("Response:")
        logging.info("-"*100)
        logging.info(response)
        logging.info("-"*100)

        # load dictionary into object
        response = Struct(response)
        output = response.choices[0].message.content
        total_tokens = response.usage.total_tokens
        return output, prompt, total_tokens
        
        # output = "Here is the output in the required format:\n\n[{\"post-title\": \"Does anyone need samples? I'm an old vendor from S\", \"post-author\": \"SupremeSmoke\", \"post-message\": \"I used to be an avid member of Silk road 1 but after losing ever\"}]"

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
            Parses the HTML and returns text for the ChatGPT to anotate.
            Also keep mapping of the text to the original HTML nodes.
        """
        with open(html_file, 'r') as f:
            html = f.read()
        soup = bs4.BeautifulSoup(html, "html.parser")
        # remove all scripts, head, style, meta, link, title, etc.
        for tag in soup.find_all(["script", "head", "style", "meta", "link", "title", "noscript", "iframe", "svg", "path", "img", "button", "input", "form", "footer", "header", "nav", "section"]):
            tag.decompose()

        # get all node containing text and keep position
        text_nodes = []
        for i, node in enumerate(soup.find_all(text=True)):
            if node.parent.name in ["style", "script", "head", "title", "meta", "[document]", "html"]:
                continue
            text_nodes.append((i, node))

        # keep at maximum one empty line between lines
        # simple automata
        last_line_empty = False
        for i in range(len(text_nodes)):
            if text_nodes[i][1] == "" or text_nodes[i][1] == " " or text_nodes[i][1] == "\n" or text_nodes[i][1] == "\t":
                if last_line_empty:
                    text_nodes[i] = None
                else:
                    last_line_empty = True
            else:
                last_line_empty = False

        text_nodes = [x for x in text_nodes if x is not None]
        # text_id_to_node = {i: node for i, node in text_nodes}
        logging.info("Found {} text nodes.".format(len(text_nodes)))

        # it helps to start at a later point in the text to eliminate navigation and other stuff
        if self.START_OFFSET > 0 and len(text_nodes)*2 > self.START_OFFSET:
            text_nodes = text_nodes[self.START_OFFSET:]
        
        if len(text_nodes) > self.MAX_INPUT_LENGTH:
            text_nodes = text_nodes[:self.MAX_INPUT_LENGTH]

        # keep only text
        texts = [str(x[1]) for x in text_nodes]
        # iterate through text and count the number of characters
        # if the number of characters exceeds the max input length, then cut the text
        for i in range(len(texts)):
            if len(texts[i]) > self.MAX_LINE_LENGTH:
                texts[i] = texts[i][:self.MAX_LINE_LENGTH]

        self.text_nodes = text_nodes
        self.texts = texts
        # join text back together
        text = "\n".join(texts)
        # if len(text) > self.MAX_INPUT_LENGTH:
        #     text = text[:self.MAX_INPUT_LENGTH]
        return text, soup, text_nodes
        
    def calculate_element_depth(self, element):
        """
            Calculates the depth of the element.
        """
        depth = 0
        # BeautifulSoup
        if hasattr(element, "parent"):
            while element.parent:
                depth += 1
                element = element.parent
        # lxml
        else:
            while element.getparent() is not None:
                depth += 1
                element = element.getparent()
        
        return depth

    def create_xPath(self, element):
        """
            Creates an XPath for the given element.
        """
        path = []
        # BeautifulSoup
        if hasattr(element, "parent"):
            while element.parent:
                if element.name is not None:
                    path.append(element.name)
                element = element.parent
        # lxml
        else:
            while element.getparent() is not None:
                if element.tag is not None:
                    path.append(element.tag)
                element = element.getparent()
        
        # reverse the path and construct xPath
        path.reverse()
        path = "/".join(path)
        path = "/" + path
        return path

    def analyze_segments(self, segments, soup: bs4.BeautifulSoup):
        if segments is None:
            return None
        
        # iterate through the segments and find the corresponding HTML elements
        # for each segment, find the corresponding HTML elements
        candidate_elements = {k: [] for k in self.segment_types}
        for segment_type in self.segment_types:
            for segment in segments:
                # skip if segment type is not in segment
                if not segment_type in segment:
                    continue

                text_to_find = segment[segment_type]
                if text_to_find is None:
                    continue

                text_to_find = text_to_find.split("\n")[0]
                if text_to_find == "":
                    continue
                
                pattern = None
                # create pattern for large-text
                if segment_type in ["post-message", "post-title"]:
                    # split text into tri-grams and find the corresponding HTML elements
                    text_to_find = text_to_find.split(" ")
                    # if the number of words is even, then use bi-grams, otherwise use tri-grams
                    N_GRAM_SIZE = 2 if len(text_to_find) % 2 == 0 else 3
                    text_to_find = [text_to_find[i:i+N_GRAM_SIZE] for i in range(0, len(text_to_find), N_GRAM_SIZE)]
                    text_to_find = [re.sub(r"[^a-zA-Z0-9\s]", "", " ".join(x)) for x in text_to_find]
                    text_to_find = "|".join(text_to_find)
                    try:
                        pattern = re.compile(text_to_find)
                    except Exception as e:
                        print("Could not compile regex pattern for text: {}".format(text_to_find))
                        continue
                
                if pattern is None:
                    # compile regex pattern to match exact text
                    pattern = re.compile(text_to_find)

                for i, node in self.text_nodes:
                    # find the exact text node (texts must be equal)
                    if not pattern.search(node):
                        continue

                    # we have text node, get the corresponding HTML element
                    aux_node = node.parent
                    # We presume that each content part is eventually wrapped in a div or h1-h6 tag
                    # Extract the most top-level tag (this is because multiple tags can be nested
                    # and represent the same content part, such as multiple <p> tags inside a <div> tag)
                    if aux_node.name not in ["div", "h1", "h2", "h3", "h4", "h5", "h6", "a", "span"] :
                        aux_node = aux_node.parent

                    element = Element(
                        tag=aux_node.name,
                        parent_tag=aux_node.parent.name,
                        grandparent_tag=aux_node.parent.parent.name,
                        depth=self.calculate_element_depth(aux_node) - 1,
                        xPath=self.create_xPath(aux_node),
                        classes=aux_node.get("class"),
                        type_id=0
                        )
                        
                    candidate_elements[segment_type].append(element)
   
                        
        # filter candidates
        filtered_candidates = {k: None for k in self.segment_types}
        for type, candidates in candidate_elements.items():
            # count candidates with the same xPath and select the one with the highest count
            xPaths = [x.xPath for x in candidates]
            xPath_counts = Counter(xPaths)
            # get the most common xPath, if multiple xPaths have the same count, then select all
            # multiple xPaths can have the same count if the text is the same, but the HTML structure is different
            # most_common_xPath = xPath_counts.most_common(1)[0][0]
            most_common_xPath_count = xPath_counts.most_common(1)[0][1]
            most_common_xPaths = [x[0] for x in xPath_counts.most_common() if x[1] == most_common_xPath_count]
            # filter candidates
            candidates = [x for x in candidates if x.xPath in most_common_xPaths]
            # if there are no candidates, then skip
            if len(candidates) == 0:
                continue
            filtered_candidates[type] = candidates

        return filtered_candidates
    
    def determine_template_elements(self, candidates, soup: bs4.BeautifulSoup):
        """
            Determines the template elements from the candidates.
        """
        html = str(soup)
        root = etree.HTML(html)
        segments = {k: [] for k in self.segment_types}
        for type, els in candidates.items():
            if els is None:
                continue
            # iterate through the elements and find the corresponding HTML elements
            for el in els:
                xPath = el.xPath
                if el.classes is not None:
                    xPath = "//{}[contains(@class, '{}')]".format(
                        el.tag,
                        " ".join(el.classes)
                    )
                elements = root.xpath(xPath)
                if len(elements) == 0:
                    continue
                # append the elements to the segments
                segments[type].append(elements) 
        
        # if there are multiple elements, use the one with the most elements
        final_segments = {k: None for k in self.segment_types}
        for type, els_lists in segments.items():
            # find the list with the most elements
            for el_list in els_lists:
                if not final_segments[type]:
                    final_segments[type] = el_list
                elif len(el_list) > len(final_segments[type]):
                    final_segments[type] = el_list
                
        return final_segments
    
    def template_from_file(self, file_path):
        """
            Generates a template from a given file.
        """
        text, soup, text_nodes = self.parse_html(file_path)
        try:
            output, prompt, total_tokens = self.analyze_text(text)
            output = self.verify_output(output)
            segments = json.loads(output)
        except Exception as e:
            print(e)
            return None, (output, prompt, total_tokens)

        # replace keys "post-title" with "post-header"
        # segments = [{k.replace("post-title", "post-header"): v for k, v in segment.items()} for segment in segments]
        candidates = self.analyze_segments(segments, soup)
        elements = self.determine_template_elements(candidates, soup)

        # if all segments have the same amount of elements, then we can use the first element
        # we found a perfect template
        perfect_match = False
        if all(len(el) == len(elements[self.segment_types[0]]) for el in elements.values()):
            perfect_match = True

        presumed_title = False
        if not perfect_match:
            # headers can often be screwed, because messages can be just reactions
            if len(elements["post-message"]) == len(elements["post-author"]):
                # presume that the longest element is the header common to all messages
                longest_el = max(elements["post-title"], key=lambda x: len(x.text))
                elements["post-title"] = [longest_el for _ in range(len(elements["post-message"]))]
                presumed_title = True


        template_proposal = {}
        # template = {}
        contents = {k: [' '.join(el.itertext()).strip() for el in v] for k, v in elements.items()}
        # if we presumed the header, then append (presumed) to the header
        if presumed_title:
            contents["post-title"] = [el + " (presumed)" for el in contents["post-title"]]

        obj_elements = []
        for type, els in elements.items():
            if len(els) > 0:
                # get lxml element
                e = els[0]
                element = ProposalElement(
                    tag=e.tag,
                    parent_tag=e.getparent().tag,
                    grandparent_tag=e.getparent().getparent().tag,
                    depth=self.calculate_element_depth(e),
                    xPath=self.create_xPath(e),
                    classes=e.get("class"),
                    type=type
                ).__dict__
                obj_elements.append(element)

        template_proposal["perfect_match"] = perfect_match
        template_proposal["contents"] = contents
        template_proposal["elements"] = obj_elements
        return template_proposal, (output, prompt, total_tokens)

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

class Struct(object):
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value

class ProposalElement:
    def __init__(self, tag, parent_tag, grandparent_tag, depth, xPath, classes, type):
        self.tag = tag
        self.parent_tag = parent_tag
        self.grandparent_tag = grandparent_tag
        self.depth = depth
        self.xPath = xPath
        self.classes = classes
        self.type = type
    

