from bs4 import BeautifulSoup
import hashlib
from .base import ParsingStrategy
import logging
from lxml import etree

class TemplatesStrategy(ParsingStrategy):

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
    
    def match_segments(self, soup):
        # iterate over segment types and find the first one that matches
        # the primary template is the post-area, if none of the templates match, return None
        segments = {k: None for k in self.segment_types}
        # iterate over templates
        for template in self.templates:
            segments_match = True
            tmp_segments = {k: None for k in self.segment_types}
            # iterate over elements in template
            for template_element in template['elements']:
                segment = self.ids_to_types[template_element['type_id']]
                xPath = template_element['xPath'].strip()
                classes = [c for c in template_element['classes'].split(' ') if c != '']
                # get html node and create text
                # TODO: this should get replaced, cuz no point in creating soup
                html = str(soup)
                root = etree.HTML(html)
                elements = root.xpath(xPath)
                # if no elements were found, the template doesn't match
                if len(elements) == 0:
                    segments_match = False
                    break

                # filter elements by classes
                filtered_elements = []
                for element in elements:
                    # if no classes were specified, add all elements
                    if len(classes) == 0:
                        filtered_elements.append(element)
                        continue
                    # if classes were specified, check if any of the classes are in the element
                    if len(classes) > 0 and any([c in element.attrib.get('class', '').split() for c in classes]):
                        filtered_elements.append(element)
                
                # if no elements were found, the template doesn't match
                if len(filtered_elements) == 0:
                    segments_match = False
                    break
                
                tmp_segments[segment] = filtered_elements
                continue
                
            if segments_match:
                segments = tmp_segments
                logging.info("Template matched, used template: {}".format(template))
                break
        
        return segments

    def parse(self, file_path):
        with open(file_path) as fd:
            contents = fd.read()

        soup = BeautifulSoup(contents, features="html.parser")
        # match segments
        segments = self.match_segments(soup)
        if segments is None:
            return None
        
        message_elements = segments['post-message']
        author_elements = segments['post-author']
        header_elements = segments['post-title']
        MD_text = ""
        content_objects = []

        if len(author_elements) != len(header_elements) and len(header_elements) == len(message_elements):
            # if the number of authors and headers does not match, but the number of headers and messages does, swap them
            author_elements = ["" for _ in range(len(message_elements))]

        for m_el, a_el, t_el in zip(message_elements, author_elements, header_elements):
            # m_el is a etree Element
            # extract all text crom element and all its children
            strings = ' '.join(m_el.itertext()).strip()
            strings = self.clear_text(strings)
            m_text = TemplatesStrategy.process_text(strings)
            # messages can be split because they contain too much text
            # strings = [s for s in m_el.strings if s.strip() != '']
            # m_text = TemplatesStrategy.process_text(" ".join(strings).strip())
            # only clear authors and headers, because they will not be analyzed by the model
            a_text = self.clear_text(' '.join(a_el.itertext()).strip(), remove_urls=False, remove_emails=False)
            t_text = self.clear_text(' '.join(t_el.itertext()).strip(), remove_urls=False, remove_emails=False)
      
            MD_text = ""
            MD_text += "## " + t_text + "\n"
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
                "content": a_text,
                "tag": 0
            }
            title_attribute = {
                "type": "post-title",
                "content": t_text,
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
