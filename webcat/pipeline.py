import os
from .parser import WebCatParser
from .analyzer import WebCatAnalyzer
import multiprocessing as mp
import logging
import time
import datasets
import time
from .models_extension import Attribute, AttributeCategory, AttributeEntity, AttributeType, Category, Content, ContentAttribute, Element, ElementType, File, NamedEntity, NamedEntityType, Template, TemplateElement

class WebCatPipeline():
    def __init__(self, db, models):
        self.db = db
        # self.initialize_parser()
        self.models = models
        self.analyzer = WebCatAnalyzer(models)
        self.batch_size = 16
        self.max_queue_size = 1000
        self.queue = mp.Queue(maxsize=self.max_queue_size)
        logging.info(f"Initialized pipeline.")

    def keep_cached_pipeline(self, models):
        old_models = self.models
        self.models = models
        if old_models != models:
            return False
        logging.info(f"Keeping cached pipeline.")
        return True
    
    def initialize_parser(self, **kwargs):
        self.parser = WebCatParser(self.db, **kwargs)

    def load_categories(self, labels):
        labels_to_ids = {}
        # try to retrieve ids from the database, if some labels are not found, create them
        # also create a mapping from labels to ids
        categories = []
        for label in labels:
            category = self.db.session.query(Category).filter(Category.name == label).first()
            if not category:
                category = Category(name=label)
                self.db.session.add(category)
                self.db.session.commit()
            categories.append(category)
            labels_to_ids[label] = category.id

        self.labels_to_ids = labels_to_ids
        self.ids_to_labels = {v: k for k, v in labels_to_ids.items()}

    def load_attribute_types(self, **kwargs):
        DEFAULT_ATTRIBUTE_TYPES = [
            {"name": "Post Author", "tag": "post-author", "analyzed": False},
            {"name": "Post Message", "tag": "post-message", "analyzed": True},
            {"name": "Post Title", "tag": "post-title", "analyzed": False}
        ]
        attribute_types_to_ids = {}
        attribute_types = self.db.session.query(AttributeType).all()
        attribute_types_list = [attribute_type.tag for attribute_type in attribute_types]
        for attribute_type in DEFAULT_ATTRIBUTE_TYPES:
            if attribute_type['tag'] not in attribute_types_list:
                attribute_type = AttributeType(name=attribute_type['name'], tag=attribute_type['tag'], analyzed=attribute_type['analyzed'])
                self.db.session.add(attribute_type)
                self.db.session.commit()
                attribute_types.append(attribute_type)

        if kwargs.get("file_type", None) == "csv":
            # some custom mapping could appear, we need to prepare db for it
            attribute_types_to_keep = kwargs.get("mapping", None)['attribute_types_to_keep']
            attribute_types_to_analyze = kwargs.get("mapping", None)['attribute_types_to_analyze']
            for attribute_type in attribute_types_to_keep:
                if attribute_type not in attribute_types_list:
                    # split by _ and capitalize first letter of each word
                    name = " ".join([word.capitalize() for word in attribute_type.split("_")])
                    attribute_type = AttributeType(name=name, tag=attribute_type, analyzed=attribute_type in attribute_types_to_analyze)
                    self.db.session.add(attribute_type)
                    self.db.session.commit()
                    attribute_types.append(attribute_type)

        for attribute_type in attribute_types:
            attribute_types_to_ids[attribute_type.tag] = attribute_type.id
        self.attribute_types_to_ids = attribute_types_to_ids
        self.attribute_tag_to_name = {attribute_type.tag: attribute_type.name for attribute_type in attribute_types}
        self.attribute_ids_to_types = {v: k for k, v in attribute_types_to_ids.items()}

    def load_named_entity_types(self):
        types_supported = self.analyzer.ner_model.get_entity_types()
        types_to_ids = {}
        # try to retrieve ids from the database, if some labels are not found, create them
        # also create a mapping from labels to ids
        entity_types = []
        for type in types_supported:
            entity_type = self.db.session.query(NamedEntityType).filter(NamedEntityType.name == type).first()
            if not entity_type:
                entity_type = NamedEntityType(name=type, tag=None)
                self.db.session.add(entity_type)
                self.db.session.commit()
            entity_types.append(entity_type)
            types_to_ids[type] = entity_type.id

        self.types_to_ids = types_to_ids
        self.ids_to_types = {v: k for k, v in types_to_ids.items()}

    def analyze_files_content(self, contents, **kwargs):
        contents = [content for content in contents if content]
        if len(contents) == 0 or contents == None:
            return [], {"total": 0,"processed": 0,"errors": 0,"duplicate": 0}

        analysis_types = ["post-message"]
        file_type = kwargs.get("file_type", "txt")
        if file_type == "csv":
            mapping = kwargs.get("mapping", {})
            analysis_types = mapping.get("attribute_types_to_analyze", ["post-message"])

        # each content in contets is a list of objects with the following structure:
        # {
        #     "file_path": str,
        #     "message: list of str,
        #     "hash": str,
        #     "header": str,
        #     "author": str,
        # }
        # filter any hashes that are already in the database
        if kwargs.get("save", True):
            hashes = [content['hash'] for content in contents]
            hashes_in_db = self.db.session.query(Content.hash).filter(Content.hash.in_(hashes)).all()
            hashes_in_db = [hash[0] for hash in hashes_in_db]
            contents_tmp = [content for content in contents if content['hash'] not in hashes_in_db]
        else:
            contents_tmp = contents

        # now filter any hashes that are duplicates
        filter_stats = {
            "total": len(contents),
            "duplicate": len(contents) - len(contents_tmp),
        }
        # remove any duplicities within the same contents
        # TODO: Isn't this useless?
        hash_index = {}
        contents_filtered = []
        for i, content in enumerate(contents_tmp):
            if content['hash'] not in hash_index:
                hash_index[content['hash']] = i
                contents_filtered.append(content)

        logging.warn(f"Filtered {filter_stats['duplicate']} duplicate hashes out of {filter_stats['total']} total hashes")
        # create a attribute: index mapping
        attributes = []
        for i, content in enumerate(contents_filtered):
            for j, attribute in enumerate(content['attributes']):
                    attributes.append({
                        "content_index": i,
                        "attribute_index": j,
                        "type": attribute['type'],
                        "content": attribute['content'],
                        "hash": content['hash'],
                        "file_path": content['file_path']
                    })

        logging.warn(f"Constructing dataset from {len(contents_filtered)} content chunks...")
        dataset = datasets.Dataset.from_list([{ "text": attribute['content'], "content_index": attribute['content_index'], "attribute_index": attribute['attribute_index'], "hash": attribute['hash'], "file_path": attribute['file_path']} for attribute in attributes if attribute['type'] in analysis_types and attribute['content'] is not None])
    
        processed_objects = []
        stats = {
            "total_contents": len(contents),
            "total_attributes": len(attributes),
            "processed_messages": 0,
            "processed_contents": 0,
            "duplicate_content": len(contents) - len(contents_filtered),
            "error": 0
        }

        for content in contents_filtered:
            for attribute in content['attributes']:
                attribute['categories'] = None
                attribute['entities'] = []

        # process entire file
        try:
            logging.info(f"Processing {len(dataset)} messages...")
            if len(dataset) == 0:
                return [], stats
            
            content_indices = dataset['content_index']
            attribute_indices = dataset['attribute_index']

            categories, entities, texts = self.analyzer.analyze_dataset(dataset, **kwargs)

            if not categories or not entities:
                return [], stats
            
            for i, (category, entity) in enumerate(zip(categories, entities)):
                contents_filtered[content_indices[i]]['attributes'][attribute_indices[i]]['categories'] = category
                contents_filtered[content_indices[i]]['attributes'][attribute_indices[i]]['entities'] = [{'name': e[0], 'type': {'name': e[1]}} for e in entity]

                stats["processed_messages"] += 1

            for i, content in enumerate(contents_filtered):
                if content == None:
                    stats["error"] += 1
                    continue
                processed_objects.append(content)
                stats["processed_contents"] += 1

        except Exception as e:
            logging.error(f"Error processing file: {content['file_path']}")
            logging.error(e)

        return processed_objects, stats

    def process_files_as_dataset(self, files_path:list, **kwargs):
        start = time.time()
        labels = kwargs["labels"] if "labels" in kwargs else None
        self.initialize_parser(**kwargs)
        self.load_categories(labels)
        self.load_named_entity_types()
        self.load_attribute_types(**kwargs)
        files_contents = self.parser.parse_files(files_path)

        analyzed_objects = []
        stats_all = {
            "total_contents": 0,
            "total_attributes": 0,
            "processed_messages": 0,
            "processed_contents": 0,
            "duplicate_content": 0,
            "error": 0
        }

        for file_content in files_contents:
            logging.info(f"Analyzing file: {file_content[0]['file_path']}")
            try:
                analyzed_content, stats = self.analyze_files_content(file_content, **kwargs)
                for key in stats_all.keys():
                    stats_all[key] += stats[key]
                if len(analyzed_content) == 0:
                    continue

                if kwargs.get("save", True):
                    saved_content = self.save_contents_to_db(analyzed_content)
                else:
                    saved_content = self.fake_save_contents_to_db(analyzed_content)

                analyzed_objects.extend(saved_content)
            except Exception as e:
                logging.error(f"Error analyzing file: {file_content[0]['file_path']}")
                logging.error(e)
                stats_all["error"] += 1

        end = time.time()
        print("Time to process files [Dataset]: ", end - start)
        serialized_content = [obj.json_serialize() for obj in analyzed_objects]
        self.db.session.close()
        return serialized_content, stats_all

    def process_raw_text(self, text, **kwargs):
        labels = kwargs["labels"] if "labels" in kwargs else None
        self.initialize_parser(**kwargs)
        self.load_categories(labels)
        self.load_named_entity_types()
        self.load_attribute_types()
        text = self.parser.parse_raw_text(text)
        categories, entities, text = self.analyzer.analyze_content([text], **kwargs)
        entities = [{'id': 0, 'name': entity[0], 'type': entity[1], 'type_id': self.types_to_ids[entity[1]]} for entity in entities[0] if entity[1] in self.types_to_ids and entity[0] != '']
        res = {
            "categories": categories[0],
            "entities": entities,
            "text": text[0]
        }
        return res
    
    def save_contents_to_db(self, contents):
        try:            # try to retrieve file from the database
            file_path = contents[0]['file_path']
            file = self.db.session.query(File).filter(File.path == file_path).first()
            if not file:
                # create new file entry in the database
                filename = os.path.basename(file_path)
                file = File(filename, file_path)
                self.db.session.add(file)
                self.db.session.commit()

            db_contents = []
            for content in contents:
                try:
                    # create new content entry in the database
                    db_content = Content(content['hash'])
                    attributes = content['attributes'] if 'attributes' in content else []
                    db_content.file = file
                    db_content.foreign_identity = content['foreign_identity'] if 'foreign_identity' in content else None
                    db_attributes = []
                    for attribute in attributes:
                        # type_id, content, tag
                        db_attribute = Attribute(self.attribute_types_to_ids[attribute['type']], attribute['content'], attribute['tag'])
                        self.db.session.add(db_attribute)
                        self.db.session.flush()
                        if attribute['categories'] != None:
                            db_attribute.categories = [AttributeCategory(db_attribute.id, self.labels_to_ids[label], conf) for label, conf in attribute['categories'].items()]
                        
                        ents = attribute['entities'] if 'entities' in attribute else []
                        ents = [ent for ent in ents if ent['type']['name'] in self.types_to_ids and ent['name'] != '' and ent['name'] != ' ']
                        named_entities = [NamedEntity(entity['name'], self.types_to_ids[entity['type']['name']]) for entity in ents]
                        db_attribute.entities = named_entities
                        self.db.session.add_all(named_entities)
                        self.db.session.flush()
                        db_attributes.append(db_attribute)

                    db_content.attributes = db_attributes

                except Exception as e:
                    self.db.session.rollback()
                    logging.error(f"Error while saving content to database: {e}")
                    return None

                self.db.session.add(db_content)
                self.db.session.commit()
                db_contents.append(db_content)
        
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error while saving content to database: {e}")
            return None
        
        return db_contents

    def fake_save_contents_to_db(self, contents):
        try:            # try to retrieve file from the database
            file_path = contents[0]['file_path']
            filename = os.path.basename(file_path)
            file = File(filename, file_path)

            db_contents = []
            for content in contents:
                try:
                    # create new content entry in the database
                    db_content = Content(content['hash'])
                    db_content.foreign_identity = content['foreign_identity'] if 'foreign_identity' in content else None
                    attributes = content['attributes'] if 'attributes' in content else []
                    db_content.file = file
                    db_attributes = []
                    for attribute in attributes:
                        db_attribute = Attribute(self.attribute_types_to_ids[attribute['type']], attribute['content'], attribute['tag'])
                        db_attribute.type = AttributeType(self.attribute_tag_to_name[attribute['type']], attribute['type'], analyzed=True)
                        if attribute['categories'] != None:
                            db_attribute.categories = [AttributeCategory(0, self.labels_to_ids[label], conf) for label, conf in attribute['categories'].items()]
                            for attribute_category in db_attribute.categories:
                                attribute_category.category = Category(self.ids_to_labels[attribute_category.category_id])
                        
                        ents = attribute['entities'] if 'entities' in attribute else []
                        ents = [ent for ent in ents if ent['type']['name'] in self.types_to_ids and ent['name'] != '' and ent['name'] != ' ']
                        named_entities = [NamedEntity(entity['name'], self.types_to_ids[entity['type']['name']]) for entity in ents]
                        for named_entity in named_entities:
                            named_entity.type = NamedEntityType(self.ids_to_types[named_entity.type_id], '')
                        db_attribute.entities = named_entities
                        db_attributes.append(db_attribute)
                    db_content.attributes = db_attributes
                
                except Exception as e:
                    logging.error(f"Error while fake saving content to database: {e}")
                    return None

                db_contents.append(db_content)
        
        except Exception as e:
            logging.error(f"Error while fake saving content to database: {e}")
            return None
        
        return db_contents