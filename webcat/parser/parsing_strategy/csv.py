from .base import ParsingStrategy
import pandas
import hashlib
import multiprocessing as mp

class ConfigMappingStrategy(ParsingStrategy):
    """
        Parsing strategy which uses the tag with the most child nodes as the main content
        to split the web page into meaningful parts.
    """
    def __init__(self, mapping) -> None:
        super().__init__()
        self.mapping = mapping
        self.expand_mapping()

    def expand_mapping(self):
        self.attribute_types = self.mapping['attribute_types_to_keep']
        self.attribute_types_to_analyze = self.mapping['attribute_types_to_analyze'][0]
        self.content_identifier_column = self.mapping['content_identifier_column']
        self.content_column = self.mapping['content_column']
        self.attribute_type_column = self.mapping['attribute_type_column']


    def parse(self, file_path):
        df = pandas.read_csv(file_path)
        print(self.mapping)

        # filter content column to contain only values from attribute_types
        rows = df[df[self.attribute_type_column].isin(self.attribute_types)]

        # take only 100 rows
        rows = rows.head(1000)
        # group by by content_identifier_column
        # iterate over each group and get the tag and content
        rows = rows.groupby(self.content_identifier_column)
        # for each group identified by content_identifier_column, create a content object
        # use multiprocessing to process each group in parallel

        with mp.Pool(mp.cpu_count()) as pool:
            content_objects = pool.starmap(ConfigMappingStrategy.construct_content_object, [(rows, self.mapping, file_path) for key, rows in rows])
        return content_objects
    
    
    @staticmethod
    def construct_content_object(rows, mapping, file_path):
        attribute_types_to_analyze = mapping['attribute_types_to_analyze']
        content_column = mapping['content_column']
        attribute_type_column = mapping['attribute_type_column']
        content_identifier_column = mapping['content_identifier_column']
        content_obj = {
                "attributes": [],
                "hash": None,
                "file_path": str(file_path),
                "foreign_identity": None,
            }
        for i, row in rows.iterrows():
            content_obj['foreign_identity'] = row[content_identifier_column]
            text_content = ParsingStrategy.clear_text(row[content_column])
            if row[attribute_type_column] in attribute_types_to_analyze:
                text_content = ParsingStrategy.process_text(text_content)
            
            content_obj['attributes'].extend(
                [
                    {
                        "type": row[attribute_type_column],
                        "content": text,
                        "tag": i
                    } for i, text in enumerate(text_content)
                ] if isinstance(text_content, list) else 
                    [{
                        "type": row[attribute_type_column],
                        "content": text_content,
                        "tag": 0
                    }]
            )

        MD_text = ""
        for attr in content_obj['attributes']:
            if attr['content'] is not None:
                MD_text += attr['content']
        content_obj['hash'] = hashlib.md5(MD_text.encode('utf-8')).hexdigest()
        return content_obj



