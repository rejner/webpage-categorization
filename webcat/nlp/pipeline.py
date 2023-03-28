import os
from .processing.parser import WebCatParser
from .processing.analyzer import WebCatAnalyzer
from api.models_extension import Template, Content, File, NamedEntity, EntityType, Category, ContentCategory
import timeit 
import multiprocessing as mp
import logging
import time
import datasets
import time
import psycopg2

class WebCatPipeline():
    def __init__(self, db):
        self.db = db
        self.initialize_parser()
        self.analyzer = WebCatAnalyzer()
        self.batch_size = 16
        self.max_queue_size = 1000
        self.queue = mp.Queue(maxsize=self.max_queue_size)
        logging.info(f"Initialized pipeline.")

    def fetch_templates(self):
        # with 
        templates = self.db.session.query(Template).all()
        return templates
    
    def initialize_parser(self):
        templates = self.fetch_templates()
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

    @DeprecationWarning
    def process_files(self, files_path:list, **kwargs):
        start = time.time()
        batch_size = kwargs.get("batch_size", self.batch_size) if "batch_size" in kwargs else self.batch_size
        labels = kwargs["labels"] if "labels" in kwargs else None
        self.load_categories(labels)
        self.load_entity_types()
        contents = self.parser.parse_files(files_path)
        contents = [content for content in contents if content]
        if len(contents) == 0 or contents == None:
            return [], {"total": 0,"processed": 0,"errors": 0,"duplicate": 0}

        # from (file_path, content (list of strings), hashes (list of hashes)) create a (file_path, content (string), hash) for each entry in contents
        # [(file_path, text, hash), (file_path, text, hash), ...]
        # create integer to path mapping to save memory when flattening the list and creating path-text pairs
        int_to_path = {i: file_path for i, (file_path, _) in enumerate(contents)}
        # invert the mapping to create a path to integer mapping
        path_to_int = {v: k for k, v in int_to_path.items()}

        # flatten the list of contents
        contents = [(path_to_int[file_path], text, hash) for file_path, content in contents for text, hash in zip(*content)]

        # filter any hashes that are already in the database
        hashes = [hash for _, _, hash in contents]
        hashes_in_db = self.db.session.query(Content.hash).filter(Content.hash.in_(hashes)).all()
        hashes_in_db = [hash[0] for hash in hashes_in_db]
        contents_filtered = [content for content in contents if content[2] not in hashes_in_db]


        # create iterator for the contents
        contents_iter = iter(contents_filtered)

        batch = contents_filtered
        if len(contents_filtered) > batch_size:
            batch = [next(contents_iter) for _ in range(batch_size)]
        
        objects = []
        stats = {
            "total": len(contents),
            "processed": 0,
            "duplicate": len(contents) - len(contents_filtered),
            "error": 0
        }
        while batch:
            inputs = [content for _, content, _ in batch if content]
            if len(inputs) == 0:
                break

            categories, entities, text = self.analyzer.analyze_content(inputs, **kwargs)
            if categories and entities and text: 
                for i in range(len(inputs)):
                    hash = batch[i][2]
                    content = self.save_content_to_db(str(int_to_path[batch[i][0]]), categories[i], entities[i], text[i], hash)
                    if content == None:
                        stats["error"] += 1
                        continue
                    cat_names = [category.category.name for category in content.categories]
                    cat_confs = [category.confidence for category in content.categories]
                    # create a dictionary of the categories and their confidence
                    cats = {cat_names[i]: cat_confs[i] for i in range(len(cat_names))}
                    objects.append({
                        "hash": hash,
                        "file": str(int_to_path[batch[i][0]]),
                        "categories": cats,
                        "entities": [entity.json_serialize() for entity in content.entities],
                        "text": text[i],
                    })
                    stats["processed"] += 1
                
            if len(inputs) < batch_size:
                break
                
            # construct the next batch, if there are no more items, then the batch will be empty
            batch = [next(contents_iter, (None, None, None)) for _ in range(batch_size)]

        end = time.time()
        print("Time to process files [custom batches]: ", end - start)
        return objects, stats

    def process_files_as_dataset(self, files_path:list, **kwargs):
        start = time.time()
        labels = kwargs["labels"] if "labels" in kwargs else None
        self.initialize_parser()
        self.load_categories(labels)
        self.load_entity_types()
        contents = self.parser.parse_files(files_path)
        contents = [content for content in contents if content]
        if len(contents) == 0 or contents == None:
            return [], {"total": 0,"processed": 0,"errors": 0,"duplicate": 0}

        # from (file_path, content (list of strings), hashes (list of hashes)) create a (file_path, content (string), hash) for each entry in contents
        # [(file_path, text, hash), (file_path, text, hash), ...]
        # create integer to path mapping to save memory when flattening the list and creating path-text pairs
        int_to_path = {i: file_path for i, (file_path, _) in enumerate(contents)}
        # invert the mapping to create a path to integer mapping
        path_to_int = {v: k for k, v in int_to_path.items()}

        # flatten the list of contents
        contents = [(path_to_int[file_path], text, hash) for file_path, content in contents for text, hash in zip(*content)]

        # filter any hashes that are already in the database
        hashes = [hash for _, _, hash in contents]
        hashes_in_db = self.db.session.query(Content.hash).filter(Content.hash.in_(hashes)).all()
        hashes_in_db = [hash[0] for hash in hashes_in_db]
        contents_tmp = [content for content in contents if content[2] not in hashes_in_db]
        # now filter any hashes that are duplicates
        filter_stats = {
            "total": len(contents),
            "duplicate": 0,
        }
        hash_index = {}
        contents_filtered = []
        for i, content in enumerate(contents_tmp):
            if content[2] not in hash_index:
                hash_index[content[2]] = i
                contents_filtered.append(content)
            else:
                filter_stats["duplicate"] += 1

        logging.warn(f"Filtered {filter_stats['duplicate']} duplicate hashes out of {filter_stats['total']} total hashes")
        
        hashes = [hash for _, _, hash in contents_filtered]
        files = [str(int_to_path[content[0]]) for content in contents_filtered]

        logging.warn(f"Constructing dataset from {len(contents_filtered)} content chunks...")

        dataset = datasets.Dataset.from_list([{ "text": content[1] } for content in contents_filtered])
        
        objects = []
        stats = {
            "total": len(contents),
            "processed": 0,
            "duplicate": len(contents) - len(contents_filtered),
            "error": 0
        }

        # process database by batches of 32
        batch_size = 32
        for i in range(0, len(contents_filtered), batch_size):
            try:
                logging.info(f"Processing batch {i} to {min(i + batch_size, len(contents_filtered))} of {len(contents_filtered)}")
                dataset_batch = dataset.select(range(i, min(i + batch_size, len(contents_filtered))))
                hashes_batch = hashes[i:min(i + batch_size, len(contents_filtered))]
                files_batch = files[i:min(i + batch_size, len(contents_filtered))]
                categories, entities, texts = self.analyzer.analyze_dataset(dataset_batch, **kwargs)
                if categories and entities:
                    # for category, entity, text, hash, file in zip(categories, entities, texts, hashes_batch, files_batch):
                    contents = self.save_content_to_db_batch(files_batch, categories, entities, texts, hashes_batch)
                    if contents == None:
                        stats["error"] += 1
                        continue

                    for j, content in enumerate(contents):
                        if content == None:
                            stats["error"] += 1
                            continue
                        cat_names = [category.category.name for category in content.categories]
                        cat_confs = [category.confidence for category in content.categories]
                        # create a dictionary of the categories and their confidence
                        cats = {cat_names[i]: cat_confs[i] for i in range(len(cat_names))}
                        objects.append({
                            "hash": hashes_batch[j],
                            "file": files_batch[j],
                            "categories": cats,
                            "entities": [entity.json_serialize() for entity in content.entities],
                            "text": content.text,
                        })
                        stats["processed"] += 1

            except Exception as e:
                logging.error(f"Error processing batch {i} to {min(i + batch_size, len(contents_filtered))} of {len(contents_filtered)}")
                logging.error(e)
                continue

        # categories, entities, texts = self.analyzer.analyze_dataset(dataset, **kwargs)
        # if categories and entities:
        #     for category, entity, text, hash, file in zip(categories, entities, texts, hashes, files):
        #         content = self.save_content_to_db(file, category, entity, text, hash)
        #         if content == None:
        #             stats["error"] += 1
        #             continue
        #         cat_names = [category.category.name for category in content.categories]
        #         cat_confs = [category.confidence for category in content.categories]
        #         # create a dictionary of the categories and their confidence
        #         cats = {cat_names[i]: cat_confs[i] for i in range(len(cat_names))}
        #         objects.append({
        #             "hash": hash,
        #             "file": file,
        #             "categories": cats,
        #             "entities": [entity.json_serialize() for entity in content.entities],
        #             "text": text,
        #         })
        #         stats["processed"] += 1

        end = time.time()
        print("Time to process files [Dataset]: ", end - start)
        return objects, stats

    def process_raw_text(self, text, **kwargs):
        labels = kwargs["labels"] if "labels" in kwargs else None
        self.load_categories(labels)
        self.load_entity_types()
        categories, entities, text = self.analyzer.analyze_content([text], **kwargs)
        entities = [{'id': 0, 'name': entity[0], 'type': entity[1], 'type_id': self.types_to_ids[entity[1]]} for entity in entities[0]]
        return {
            "categories": categories[0],
            "entities": entities,
            "text": text[0]
        }
    
    def save_content_to_db(self, file_path, categories, entities, text, hash):
        try:
            # try to retrieve file from the database
            file = self.db.session.query(File).filter(File.path == file_path).first()
            if not file:
                # create new file entry in the database
                filename = os.path.basename(file_path)
                file = File(filename, file_path)
                self.db.session.add(file)
                self.db.session.commit()

            # create new content entry in the database
            content = Content(file.id, text, hash)
            content_categories = [ContentCategory(content.id, self.labels_to_ids[label], conf) for label, conf in categories.items()]
            content.categories = content_categories
            ents = []
            if entities:
                if isinstance(entities[0], tuple):
                    ents = [NamedEntity(entity[0], self.types_to_ids[entity[1]]) for entity in entities if entity[1] in self.types_to_ids]
                if isinstance(entities[0], dict):
                    ents = [NamedEntity(entity["word"], self.types_to_ids[entity["entity_group"]]) for entity in entities]

            content.entities = ents
            self.db.session.add(content)
            self.db.session.commit()
        
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error while saving content to database: {e}")
            return None
        
        return content
    
    def save_content_to_db_batch(self, file_paths, categories, entities, texts, hashes):
        try:
            # create new file entries in the database
            files = []
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                file = File(filename, file_path)
                self.db.session.add(file)
                files.append(file)
            self.db.session.commit()

            # create new content entries in the database
            contents = []
            for file, category, entity, text, hash in zip(files, categories, entities, texts, hashes):
                try:
                    content = Content(file.id, text, hash)
                    content_categories = [ContentCategory(content.id, self.labels_to_ids[label], conf) for label, conf in category.items()]
                    content.categories = content_categories
                    content.entities = [NamedEntity(entity[0], self.types_to_ids[entity[1]]) for entity in entity]
                    self.db.session.add(content)
                    self.db.session.commit()
                    contents.append(content)
                
                except psycopg2.errors.UniqueViolation:
                    self.db.session.rollback()
                    logging.error(f"Content with hash {hash} already exists in the database.")
                    contents.append(None)
                    continue
                
                except Exception as e:
                    self.db.session.rollback()
                    logging.error(f"Error while saving content to database: {e}")
                    contents.append(None)
                    continue
                
        
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error while saving content to database: {e}")
            return None
        
        return contents
