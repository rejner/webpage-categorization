import os
from .processing.parser import WebCatParser
from .processing.analyzer import WebCatAnalyzer
from api.models_extension import *
import timeit 
import multiprocessing as mp
import logging
import time
import datasets
import time
import psycopg2

class WebCatPipeline():
    def __init__(self, db, models):
        self.db = db
        self.initialize_parser()
        self.analyzer = WebCatAnalyzer(models)
        self.batch_size = 16
        self.max_queue_size = 1000
        self.queue = mp.Queue(maxsize=self.max_queue_size)
        logging.info(f"Initialized pipeline.")

    def fetch_templates(self, version=2):
        templates = []
        if version == 1:
            templates = self.db.session.query(Template).all()
        
        if version == 2:
            templates = self.db.session.query(Template_v2).all()

        templates = [template.json_serialize() for template in templates]
        return templates
    
    def initialize_parser(self):
        templates = self.fetch_templates(version=2)
        self.parser = WebCatParser(templates)

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

    def load_entity_types(self):
        types_supported = self.analyzer.ner_model.get_entity_types()
        types_to_ids = {}
        # try to retrieve ids from the database, if some labels are not found, create them
        # also create a mapping from labels to ids
        entity_types = []
        for type in types_supported:
            entity_type = self.db.session.query(EntityType).filter(EntityType.name == type).first()
            if not entity_type:
                entity_type = EntityType(name=type, tag=None)
                self.db.session.add(entity_type)
                self.db.session.commit()
            entity_types.append(entity_type)
            types_to_ids[type] = entity_type.id

        self.types_to_ids = types_to_ids

    def analyze_files_content(self, contents, **kwargs):
        contents = [content for content in contents if content]
        if len(contents) == 0 or contents == None:
            return [], {"total": 0,"processed": 0,"errors": 0,"duplicate": 0}

        # each content in contets is a list of objects with the following structure:
        # {
        #     "file_path": str,
        #     "message: list of str,
        #     "hash": str,
        #     "header": str,
        #     "author": str,
        # }
        # filter any hashes that are already in the database
        hashes = [content['hash'] for content in contents]
        hashes_in_db = self.db.session.query(Content_v2.hash).filter(Content_v2.hash.in_(hashes)).all()
        hashes_in_db = [hash[0] for hash in hashes_in_db]
        contents_tmp = [content for content in contents if content['hash'] not in hashes_in_db]
        # now filter any hashes that are duplicates
        filter_stats = {
            "total": len(contents),
            "duplicate": len(contents) - len(contents_tmp),
        }
        hash_index = {}
        contents_filtered = []
        for i, content in enumerate(contents_tmp):
            if content['hash'] not in hash_index:
                hash_index[content['hash']] = i
                contents_filtered.append(content)

        logging.warn(f"Filtered {filter_stats['duplicate']} duplicate hashes out of {filter_stats['total']} total hashes")
        # create a message: index mapping
        messages = []
        for i, content in enumerate(contents_filtered):
            for message in content['message']:
                messages.append({
                    "message": message,
                    "content_row": i,
                    "hash": content['hash'],
                    "file_path": content['file_path']
                })

        logging.warn(f"Constructing dataset from {len(contents_filtered)} content chunks...")
        dataset = datasets.Dataset.from_list([{ "text": message['message'], "content_row": message['content_row'], "hash": message['hash'], "file_path": message['file_path']} for message in messages])
    
        processed_objects = []
        stats = {
            "total_contents": len(contents),
            "total_messages": len(messages),
            "processed_messages": 0,
            "processed_contents": 0,
            "duplicate_content": len(contents) - len(contents_filtered),
            "error": 0
        }

        # add the categories and entities to the filtered contents andd initialize with []
        for content in contents_filtered:
            content['categories'] = []
            content['entities'] = []


        # process entire file
        try:
            logging.info(f"Processing {len(messages)} messages...")
            if len(messages) == 0:
                return [], stats
            
            rows = dataset['content_row']
            categories, entities, texts = self.analyzer.analyze_dataset(dataset, **kwargs)

            if not categories or not entities:
                return [], stats
            
            for i, (category, entity) in enumerate(zip(categories, entities)):
                contents_filtered[rows[i]]['categories'].append(category)
                contents_filtered[rows[i]]['entities'].append([{'name': e[0], 'type': {'name': e[1]}} for e in entity])
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
        self.initialize_parser()
        self.load_categories(labels)
        self.load_entity_types()
        files_contents = self.parser.parse_files(files_path)

        analyzed_objects = []
        stats_all = {
            "total_contents": 0,
            "total_messages": 0,
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
                saved_content = self.save_contents_to_db(analyzed_content)
                analyzed_objects.extend(saved_content)
            except Exception as e:
                logging.error(f"Error analyzing file: {file_content[0]['file_path']}")
                logging.error(e)
                stats_all["error"] += 1

        end = time.time()
        print("Time to process files [Dataset]: ", end - start)
        return [obj.json_serialize() for obj in analyzed_objects], stats_all
    
    def process_raw_text(self, text, **kwargs):
        labels = kwargs["labels"] if "labels" in kwargs else None
        self.load_categories(labels)
        self.load_entity_types()
        text = self.parser.parse_raw_text(text)
        categories, entities, text = self.analyzer.analyze_content([text], **kwargs)
        print(categories)
        print(entities)
        print(text)
        entities = [{'id': 0, 'name': entity[0], 'type': entity[1], 'type_id': self.types_to_ids[entity[1]]} for entity in entities[0]]
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
                    db_content = Content_v2(content['hash'], content['author'], content['header'])
                    db_content.file = file
                    messages = []
                    for cats, ents, text in zip(content['categories'], content['entities'], content['message']):
                        message = Message_v2(text)
                        self.db.session.add(message)
                        self.db.session.flush()
                        message.categories = [MessageCategory_v2(message.id, self.labels_to_ids[label], conf) for label, conf in cats.items()]
                        ents = [ent for ent in ents if ent['type']['name'] in self.types_to_ids and ent['name'] != '' and ent['name'] != ' ']
                        named_entities = [NamedEntity(entity['name'], self.types_to_ids[entity['type']['name']]) for entity in ents]
                        message.entities = named_entities
                        self.db.session.add_all(named_entities)
                        self.db.session.flush()
                        # message.entities = [MessageEntity_v2(message.id, entity.id) for entity in named_entities]
                        messages.append(message)
                    db_content.messages = messages
                
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
