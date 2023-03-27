from flask_restful import Resource, reqparse, request
from database import db
from models_extension import *
import time

class WebCatDataProvider(Resource):
    """
    This class is responsible for providing data to the frontend.
    The frontend can ask for data with the filters it wants.
    Filters can be:
    - category/ies (list of categories)
    - category confidence value threshold
    - entity type (list of entity types like person, location, etc.)
    - entity confidence value threshold
    - entity value (list of entity values) - actual entity text (name)
    - file name (list of file names)
    - file path (list of file paths)
    """
    def __init__(self):
        super().__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('categories', type=str, action='append')
        self.parser.add_argument('cat_threshold', type=float, default=0.0)
        self.parser.add_argument('entity_types', type=str, action='append')
        self.parser.add_argument('ent_threshold', type=float, default=0.0)
        self.parser.add_argument('entity_values', type=str, action='append')
        self.parser.add_argument('file_names', type=str, action='append')
        self.parser.add_argument('file_paths', type=str, action='append')

        self.file_cache = {}

    # def process_request(self, args): # My shitty code
    #     # validate and process args
    #     categories = args['categories'] or []
    #     cat_threshold = args['cat_threshold']
    #     entity_types = args['entity_types'] or []
    #     ent_threshold = args['ent_threshold']
    #     entity_values = args['entity_values'] or []
    #     file_names = args['file_names'] or []
    #     file_paths = args['file_paths'] or []

    #     # implement data filtering based on the above parameters
    #     # and return the filtered data
        
    #     # create query for each filter and combine them with AND
    #     if categories and 'all' not in categories:
    #         category_query = db.session.query(Content).filter(Content.categories.any(ContentCategory.category.has(Category.name.in_(categories))))
    #     else:
    #         category_query = db.session.query(Content).filter(Content.categories.any())

    #     if entity_types and 'all' not in entity_types:
    #         entity_query = db.session.query(Content).filter(Content.entities.any(NamedEntity.type.has(EntityType.name.in_(entity_types))))
    #     else:
    #         entity_query = db.session.query(Content).filter(Content.entities.any())

    #     if cat_threshold > 0 and categories:
    #         # remove categories with confidence value lower than threshold
    #         tmp = []
    #         for content in category_query:
    #             required_categories = [category for category in content.categories if category.category.name in categories]
    #             # if all required categories have confidence value lower than threshold, remove the content object
    #             if all([category.confidence < cat_threshold for category in required_categories]):
    #                 tmp.append(content)

    #         # remove content objects from query which appear in tmp
    #         category_query = category_query.filter(~Content.id.in_([c.id for c in tmp]))

    #     # merge objects from both queries (intersect)
    #     query = category_query.intersect(entity_query)
    #     return query.all()

    def process_request(self, args):
        # validate and process args
        categories = args.get('categories', [])
        cat_threshold = args.get('cat_threshold', 0)
        entity_types = args.get('entity_types', [])
        ent_threshold = args.get('ent_threshold', 0)
        entity_values = args.get('entity_values', [])
        file_names = args.get('file_names', [])
        file_paths = args.get('file_paths', [])

        # construct base query for filtering
        query = db.session.query(Content)

        # apply filters for categories and entities
        if categories and 'all' not in categories:
            category_query = query.join(ContentCategory).join(Category).filter(Category.name.in_(categories))
            if cat_threshold > 0:
                category_query = category_query.filter(ContentCategory.confidence >= cat_threshold)
            query = query.intersect(category_query)

        if entity_types and 'all' not in entity_types:
            entity_query = query.join(Content.entities).join(NamedEntity.type).filter(EntityType.name.in_(entity_types))
            if ent_threshold > 0:
                entity_query = entity_query.filter(NamedEntity.confidence >= ent_threshold)
            query = query.intersect(entity_query)

        # apply filters for entity values, file names, and file paths
        # if entity_values:
        #     query = query.filter(Content.content_text.contains(entity_values))
        # if file_names:
        #     query = query.filter(Content.file_name.in_(file_names))
        # if file_paths:
        #     query = query.filter(Content.file_path.in_(file_paths))

        # execute the query and return the results
        return query.all()

    def serialize_content(self, content: Content):
        cat_names = [category.category.name for category in content.categories]
        cat_confs = [category.confidence for category in content.categories]
        # create a dictionary of the categories and their confidence
        categories = {cat_names[i]: cat_confs[i] for i in range(len(cat_names))}
        try:
            # try to get the file from cache
            file = self.file_cache[content.file_id]
        except KeyError:
            # if not in cache, get it from the database
            file = db.session.query(File).filter_by(id=content.file_id).first()
            self.file_cache[content.file_id] = file

        return {
            "id": content.id,
            'file': file.path,
            "categories": categories,
            "entities": [entity.json_serialize() for entity in content.entities],
            "text": content.text
        }

    # Get returns all possible categories and entity types
    def get(self):
        categories = db.session.query(Category.name).all()
        categories = [c[0] for c in categories]
        entity_types = db.session.query(EntityType.name).all()
        entity_types = [e[0] for e in entity_types]
        return {'categories': categories, 'entity_types': entity_types}

    def post(self):
        args = self.parser.parse_args()
        start_2 = time.time()
        filtered_data = self.process_request(args)
        end_2 = time.time()
        print("Time for process_request: ", end_2 - start_2)
        return [self.serialize_content(content) for content in filtered_data]

    # delete will be sent as a delete request with id in the url
    def delete(self):
        id = request.json['id']
        if id is None:
            return {'error': "No id provided"}, 400
        try:
            content = db.session.query(Content).get(id)
            db.session.delete(content)
            db.session.commit()
        except Exception as e:
            return {'error': str(e)}, 400
        
        return "Success", 200