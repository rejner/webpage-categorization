import re
from collections import Counter
from bs4 import BeautifulSoup
import hashlib
from .base import ParsingStrategy

class TemplatesStrategy(ParsingStrategy):
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
        self.templates = templates
        # iterate all templates and get all segment types
        self.segment_types = []
        for template in templates:
            for element in template['elements']:
                if element['type']['tag'] not in self.segment_types:
                    self.segment_types.append((element['type']['tag'], element['type']['id']))
        
        self.ids_to_types = {k[1]: k[0] for k in self.segment_types}
        self.segment_types = [k[0] for k in self.segment_types]

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

    def parse(self, file_path):
        with open(file_path) as fd:
            contents = fd.read()

        soup = BeautifulSoup(contents, features="html.parser")
        # if content is not parsable return None

        # match segments
        segments = self.match_segments(soup)

        # Find all the tags in the Beautiful Soup object
        if segments is None:
            return None
        
        message_elements = segments['post-message']
        author_elements = segments['post-author']
        header_elements = segments['post-title']
        MD_text = ""
        content_objects = []

        content_len = max(len(message_elements), len(author_elements), len(header_elements))
        for elements in [message_elements, author_elements, header_elements]:
            # length of all elements must be the same, or 0 (if no elements were found)
            assert len(elements) == content_len or len(elements) == 0

        for m_el, a_el, h_el in zip(message_elements, author_elements, header_elements):
            # messages can be split because they contain too much text
            strings = [s for s in m_el.strings if s.strip() != '']
            m_text = TemplatesStrategy.process_text(" ".join(strings).strip())
            # only clear authors and headers, because they will not be analyzed by the model
            a_text = self.clear_text(a_el.text, remove_urls=False, remove_emails=False)
            h_text = self.clear_text(h_el.text, remove_urls=False, remove_emails=False)
      
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
            message_attributes = [{
                "type": "post-message",
                "content": text,
                "tag": i
            } for i, text in enumerate(m_text)]
            author_attribute = {
                "type": "post-author",
                "content": h_text,
                "tag": 0
            }
            title_attribute = {
                "type": "post-title",
                "content": a_text,
                "tag": 0
            }
            content_objects.append({
                "attributes": [
                    author_attribute,
                    title_attribute,
                    *message_attributes
                ],
                "hash": hsh,
                "file_path": str(file_path),
            })

        return content_objects

if __name__ == "__main__":
    strategy = TemplatesStrategy(
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