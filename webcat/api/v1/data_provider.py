from flask_restful import Resource, reqparse, request
from database import db
from models_extension import *
import time
from sqlalchemy.orm import contains_eager

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

    def process_request(self, args):
        # validate and process args
        categories = args.get('categories', [])
        cat_threshold = args.get('cat_threshold', 0)
        entity_types = args.get('entity_types', [])
        ent_threshold = args.get('ent_threshold', 0)
        entity_values = args.get('entity_values', [])
        file_names = args.get('file_names', [])
        file_paths = args.get('file_paths', [])
        
        # build the query
        query = db.session.query(Content_v2)
        query = query.join(ContentMessage_v2).join(Message_v2).join(MessageCategory_v2, Message_v2.id == MessageCategory_v2.message_id).join(Category, MessageCategory_v2.category_id == Category.id)
        # apply filters for categories and entities
        if categories:
            if 'all' not in categories:
                # filter by categories
                category_query = query.filter(Category.name.in_(categories))
                if cat_threshold > 0:
                    category_query = category_query.filter(MessageCategory_v2.confidence >= cat_threshold)
                query = query.intersect(category_query)

        if entity_types:
            if 'all' not in entity_types:
                # filter by entity types
                entity_query = query.join(ContentMessage_v2).join(Message_v2, Message_v2.id == ContentMessage_v2.message_id).join(MessageEntity_v2, MessageEntity_v2.message_id == Message_v2.id).join(NamedEntity, NamedEntity.id == MessageEntity_v2.entity_id).join(EntityType, EntityType.id == NamedEntity.type_id).filter(EntityType.name.in_(entity_types))
                if ent_threshold > 0:
                    entity_query = entity_query.filter(NamedEntity.confidence >= ent_threshold)
                query = query.intersect(entity_query)

        # execute the query and return the results
        return query.all()

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
        return [data.json_serialize() for data in filtered_data]

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