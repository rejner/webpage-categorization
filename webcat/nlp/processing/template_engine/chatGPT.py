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
        self.MAX_INPUT_LENGTH = 4000
        self.MAX_LINE_LENGTH = 256
        self.PROMPT_START = "Analyze the text I give you and output only a JSON array with the found segments \"post-header\", \"post-author\" and \"post-message\". Do not output anything else. I need you to segment this piece of text, a collection of forum posts. The value of the segment should be the exact matched text. Try to extract at least 3 posts. The input is:\n"
        self.SYSTEM_PROMPT = "You are a server for analyzing text data, responding in JSON format."
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
        response = RESPONSE
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=payload,
        # )
        # print("Response:")
        # print("-"*100)
        # print(response)
        # print("-"*100)

        # load dictionary into object
        response = Struct(response)
        output = response.choices[0].message.content
        return json.loads(output)

    def parse_html(self, html_file):
        """
            Parses the HTML and returns text.
        """
        with  open(html_file, 'r') as f:
            html = f.read()
        soup = bs4.BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        text = text.split("\n")

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
                    # split text into tri-grams and find the corresponding HTML elements
                    text_to_find = text_to_find.split(" ")
                    text_to_find = [text_to_find[i:i+3] for i in range(0, len(text_to_find), 3)]
                    text_to_find = [" ".join(x) for x in text_to_find]
                    text_to_find = "|".join(text_to_find)
                    # compile regex pattern for tri-grams
                    pattern = re.compile(text_to_find)
                    elements = [el.parent for el in soup.findAll(text=pattern)]
                    if elements:
                        candidate_elements[segment_type].append(elements)
        
        # construct a list of candidate elements for each segment from special objects
        candidates = {k: [] for k in self.segment_types}
        for type, elements in candidate_elements.items():
            for els in elements:
                tmp = []
                for el in els:
                    tmp.append(
                        TemplateElements(
                            tag=el.name,
                            parent_tag=el.parent.name,
                            grandparent_tag=el.parent.parent.name,
                            depth=self.calculate_element_depth(el),
                        )
                    )
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
                    break

            # find all elements that match the template element
            els = soup.findAll(tag)
            els = [el for el in els if el.parent.name == parent_tag and el.parent.parent.name == grandparent_tag and self.calculate_element_depth(el) == depth]
            elements[type] = els
        
        return elements
    
    def template_from_file(self, file_path):
        """
            Generates a template from a given file.
        """
        text, soup = self.parse_html(file_path)
        segments = self.analyze_text(text)
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

        template_proposal = {}
        # template = {}
        contents = {k: [el.text for el in v] for k, v in elements.items()}
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


"""
'\n\n\n\n  \n\n\n\nBungee54 State of Operations (Page 1) — General Discussion — Bungee54 Member Assembly\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nLogged in as simurgh.\n\nIndex\nNews\nUser list\nWebchat (2)\nSearch\nBitcoin (340 USD)\nProfile\nLogout\nB54.market\nB54.SR2\nB54.AG\nB54.BB\nB54.C9\n\n\n\n\n\n\nSkip to forum content\n\n\n\nBungee54 State of Operations\n\nBungee54 Member Assembly  →\xa0General Discussion  →\xa0Bungee54 State of Operations \n\n\nPages 1\nPost reply\n\n\nRSS topic feed Subscribe\nPosts: 55\n\n\n\n\n1 Topic by Calico Jack 2014-10-21 23:45:42\n\n\n\n\nCalico Jack\nBastard Administrator from Hell\nOffline\n\n\nRegistered: 2013-10-09\nPosts: 196\n\n\n\nTopic: Bungee54 State of Operations\n\nTo all of our friends, valued customers, competitors, partners,\xa0 haters and trolls of Bungee54!Please read the following announcement carefully and in it\'s entirety:The Bungee54 Team is going through a transition that will involve us taking a step back int\nBAFH"Cryptography is Freedom"\n\n\n\n\n\nBitmessage\xa0Calico Jack PM\nReport Post 1 Quote Post 1\n\n\n\n\n\n2 Reply by Fahshizzle 2014-10-22 00:17:28\n\n\n\n\nFahshizzle\nMember\nOffline\n\n\nRegistered: 2013-12-29\nPosts: 35\n\n\n\nRe: Bungee54 State of Operations\n\nthanks for the heads up, certainly makes me feel better about all the FUD thats been going around.sounds like ill need start shopping around for a new vendor  if youre still willing to work with me PM please otherwise, do you have any suggestions for the c\n\n\n\n\n\nPM\nReport Post 2 Quote Post 2\n\n\n\n\n\n3 Reply by drmindbender 2014-10-22 02:03:36\n\n\n\n\ndrmindbender\nNewbie\nOffline\n\n\nRegistered: 2014-08-21\nPosts: 9\n\n\n\nRe: Bungee54 State of Operations\n\nDespite my latest package order not having arrived for more than 2 weeks... and I\'m going to assume it was probably seized in the next day or 2, I am very happy to have read your State of Operations.\xa0 This goes very closely with how I personally feel suppl\n\n\n\n\n\nPM\nReport Post 3 Quote Post 3\n\n\n\n\n\n4 Reply by Axwell 2014-10-22 02:13:25\n\n\n\n\nAxwell\nNewbie\nOffline\n\n\nRegistered: 2014-10-02\nPosts: 9\n\n\n\nRe: Bungee54 State of Operations\n\nBungee team,I\'ve only ordered from you off of Agora under a different name, but I just wanted to let you know that some of us will always support you. Even with the recent delays all of my packages arrived. I wish the team the best with a much deserved bre\n\n\n\n\n\nPM\nReport Post 4 Quote Post 4\n\n\n\n\n\n5 Reply by hosemonster 2014-10-22 02:15:34\n\n\n\n\nhosemonster\nJunior Member\nOffline\n\n\nRegistered: 2014-08-30\nPosts: 72\n\n\n\nRe: Bungee54 State of Operations\n\nWell damn.\xa0 Your final legacy for this part of your journey will be written in the next two months.\xa0 If you take care of every customer as you always have, you will shine better than any other.\xa0 If you don\'t, may Karma eat you alive.\n\n\n\n\n\nPM\nReport Post 5 Quote Post 5\n\n\n\n\n\n6 Reply by LordCynth 2014-10-22 02:21:00\n\n\n\n\nLordCynth\nMember\nOffline\n\n\nRegistered: 2014-09-28\nPosts: 33\n\n\n\nRe: Bungee54 State of Operations\n\nHope to see you back in the full swing of things soon, also hope to talk about my reship soon \n\n\n\n\n\nPM\nReport Post 6 Quote Post 6\n\n\n\n\n\n7 Reply by homer simpson 2014-10-22 06:22:56\n\n\n\n\n\nhomer simpson\nSenior Member\nOffline\n\n\nFrom: Springfield\nRegistered: 2013-10-10\nPosts: 213\n\n\n\nRe: Bungee54 State of Operations\n\nglad to hear from you Jack - take all the time you need. the great majority of us in this community have been well taken care of by you and wish you the best of luck moving forward\nLong-time Bungee54 customer - feel free to ask me anything!The bitmessage address I had tied to this account is no longer active.\n\n\n\n\n\nBitmessage\xa0homer simpson PGP PM\nReport Post 7 Quote Post 7\n\n\n\n\n\n8 Reply by verzero 2014-10-22 07:25:03\n\n\n\n\nverzero\nJunior Member\nOffline\n\n\nRegistered: 2014-04-28\nPosts: 75\n\n\n\nRe: Bungee54 State of Operations\n\nCouldn\'t ask for a better speech. This is exact kind of mature and well thought out response I was waiting for. Bungee has pull through for us from time and time again. They deserve this break and from it, so they can begin anew. Thanks for all the hard wo\n\n\n\n\n\nPM\nReport Post 8 Quote Post 8\n\n\n\n\n\n9 Repl'
"""

"""
'\n\n\n\n\n\n\n\n\n\n\nTortuga • View topic - Who´s running this?\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nTortuga\nForum\nSkip to content\n\n\n\n\n\n\nAdvanced search\n\n\n\n\n\n\n\n\nBoard index ‹ Tortuga ‹ General\nChange font size\nPrint view\n\n\nFAQ\nRegister\nLogin\n\n\n\n\n\n\nWho´s running this?\n\n\n\nPost a reply\n\n\n\n\n\n\n\n\n\n\n\n\n\t\t\t10 posts\n\t\t\t • Page 1 of 1\n\n\n\n\n\n\nWho´s running this?\nby ScReaper » Tue Dec 24, 2013 8:39 pm \nStep up, declare your role.The darkmarkets is bleeding and there´s no trust left... why should i sell my shit on your market and how can you guarantee you wont run with the wallets?\n\n\n\nScReaper\n\n\xa0\nPosts: 1Joined: Tue Dec 24, 2013 8:38 pm\n\nTop\n\n\n\n\n\n\nRe: Who´s running this?\nby brickmaster » Tue Dec 24, 2013 8:59 pm \nGood Point, I\'d like to hear a response to that question. I\'m feeling kind of iffy about selling on this site especially since there are little to no vendors and no sign of customers.\n\n\n\nbrickmaster\n\n\xa0\nPosts: 1Joined: Tue Dec 24, 2013 7:33 pm\n\nTop\n\n\n\n\n\n\nRe: Who´s running this?\nby J0K3R » Tue Dec 24, 2013 9:37 pm \nScReaper wrote:Step up, declare your role.The darkmarkets is bleeding and there´s no trust left... why should i sell my shit on your market and how can you guarantee you wont run with the wallets?I can\'t guarantee anything, but:1. I\'am old school guy and I\n\n\n\nJ0K3R\n\nSite Admin\n\xa0\nPosts: 13Joined: Sun Dec 15, 2013 8:09 pm\n\nTop\n\n\n\n\n\n\nRe: Who´s running this?\nby Perico » Wed Dec 25, 2013 1:27 pm \nI noticed the "Help" is blank.  What is Tortuga pegging BTC to ?\n\n\n\nPerico\n\n\xa0\nPosts: 7Joined: Wed Dec 25, 2013 1:11 pm\n\nTop\n\n\n\n\n\n\nRe: Who´s running this?\nby Scarface » Wed Dec 25, 2013 2:00 pm \nPerico wrote:I noticed the "Help" is blank.  What is Tortuga pegging BTC to ?Hey,The conversion process is automatic, exchange rate(from GOX) updated in every 10 min.S\n\n\n\nScarface\n\n\xa0\nPosts: 2Joined: Mon Dec 16, 2013 11:49 am\n\nTop\n\n\n\n\n\n\nRe: Who´s running this?\nby Perico » Wed Dec 25, 2013 7:42 pm \nI also noticed when I click on Sell>Add New>  Nothing happens.  I cannot add listings?\n\n\n\nPerico\n\n\xa0\nPosts: 7Joined: Wed Dec 25, 2013 1:11 pm\n\nTop\n\n\n\n\n\n\nRe: Who´s running this?\nby J0K3R » Wed Dec 25, 2013 10:52 pm \nPerico wrote:I also noticed when I click on Sell>Add New>  Nothing happens.  I cannot add listings?Browser/Tor version/Operating system/Tablet or PC?We tested all functions before we started the site, but only on win7/ubuntu with the newest TOR\n\n\n\nJ0K3R\n\nSite Admin\n\xa0\nPosts: 13Joined: Sun Dec 15, 2013 8:09 pm\n\nTop\n\n\n\n\n\n\nRe: Who´s running this?\nby J0K3R » Wed Dec 25, 2013 11:13 pm \nPerico wrote:I also noticed when I click on Sell>Add New>  Nothing happens.  I cannot add listings?I\'ve changed the button, please try again.\n\n\n\nJ0K3R\n\nSite Admin\n\xa0\nPosts: 13Joined: Sun Dec 15, 2013 8:09 pm\n\nTop\n\n\n\n\n\n\nRe: Who´s running this?\nby chylan » Thu Dec 26, 2013 12:35 am \nAnother new site? Fuck i hope this place ends up being legit, tormarket and sheep were both good sites untilthey fucked everyone. Mister joker, i sincerely ask what your motorvations  are?\n\n\n\nchylan\n\n\xa0\nPosts: 1Joined: Thu Dec 26, 2013 12:27 am\n\nTop\n\n\n\n\n\n\nRe: Who´s running this?\nby Perico » Thu Dec 26, 2013 5:22 am \nThe trick would be to not have any bitcoins you cannot afford to loose in escrow.  After proving oneself worthy of FE buyers will oblige, specially loyal one\'s.  Encrypt everything.Cross fingers.\n\n\n\nPerico\n\n\xa0\nPosts: 7Joined: Wed Dec 25, 2013 1:11 pm\n\nTop\n\n\n\n\n\nDisplay posts from previous: All posts1 day7 days2 weeks1 month3 months6 months1 year\nSort by AuthorPost timeSubject AscendingDescending \n\n\n\n\n\nPost a reply\n\n\n\t\t\t10 posts\n\t\t\t • Page 1 of 1\n\n\nReturn to General\n\n\nJump to:\n\nSelect a forum\n------------------\nTortuga\n\xa0 \xa0General\n\xa0 \xa0Selling and Shipping\n\xa0 \xa0Buying and Receiving\n\xa0 \xa0Stealth and Security\n\xa0 \xa0Offtopic\n\n\n\n\n\n\n\n\n\nBoard index\nThe team • Delete all board cookies • All times are UTC \n\n\n\nPowered by phpBB® Forum Software © phpBB Group\n\t\t\n\t\n\n\n\n\n\n\n'

"""


        # output = r"""
        # [
        #     {
        #         "post-header": "Bungee54 State of Operations",
        #         "post-author": "Calico Jack",
        #         "post-message": "To all of our friends, valued customers, competitors, partners, haters and trolls of Bungee54!Please read the following announcement carefully and in it's entirety:The Bungee54 Team is going through a transition that will involve us taking a step back int\nBAFH\"Cryptography is Freedom\""
        #     },
        #     {
        #         "post-header": "Bungee54 State of Operations",
        #         "post-author": "Fahshizzle",
        #         "post-message": "thanks for the heads up, certainly makes me feel better about all the FUD thats been going around.sounds like ill need start shopping around for a new vendor  if youre still willing to work with me PM please otherwise, do you have any suggestions for the c"
        #     },
        #     {
        #         "post-header": "Bungee54 State of Operations",
        #         "post-author": "drmindbender",
        #         "post-message": "Despite my latest package order not having arrived for more than 2 weeks..."
        #     }
        # ]
        # """
        # output = r"""
        # [
        #     {
        #         "post-header": "Who´s running this?",
        #         "post-author": "ScReaper",
        #         "post-message": "Step up, declare your role.The darkmarkets is bleeding and there´s no trust left... why should i sell my shit on your market and how can you guarantee you wont run with the wallets?"
        #     },
        #     {
        #         "post-header": "Who´s running this?",
        #         "post-author": "brickmaster",
        #         "post-message": "Good Point, I'd like to hear a response to that question. I'm feeling kind of iffy about selling on this site especially since there are little to no vendors and no sign of customers."
        #     },
        #     {
        #         "post-header": "Who´s running this?",
        #         "post-author": "J0K3R",
        #         "post-message": "ScReaper wrote:Step up, declare your role.The darkmarkets is bleeding and there´s no trust left... why should i sell my shit on your market and how can you guarantee you wont run with the wallets?I can't guarantee anything"
        #     }
        # ]
        
        # """

# real GPT answer
'[\n  {\n    "post-header": "Topic: Bungee54 State of Operations",\n    "post-author": "Calico Jack",\n    "post-message": "To all of our friends, valued customers, competitors, partners,  haters and trolls of Bungee54!Please read the following announcement carefully and in it\'s entirety:The Bungee54 Team is going through a transition that will involve us taking a step back int\\nBAFH\\"Cryptography is Freedom\\""\n  },\n  {\n    "post-header": "Re: Bungee54 State of Operations",\n    "post-author": "Fahshizzle",\n    "post-message": "thanks for the heads up, certainly makes me feel better about all the FUD thats been going around.sounds like ill need start shopping around for a new vendor  if youre still willing to work with me PM please otherwise, do you have any suggestions for the c"\n  },\n  {\n    "post-header": "Re: Bungee54 State of Operations",\n    "post-author": "drmindbender",\n    "post-message": "Despite my latest package order not having arrived for more than 2 weeks... and I\'m going to assume it was probably seized in the next day or 2, I am very happy to have read your State of Operations.\\u00a0 This goes very closely with how I personally feel suppl"\n  }\n]'

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