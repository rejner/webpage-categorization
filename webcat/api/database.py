from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# def init_db(app):
#     # from db_models.category import Category
#     # from db_models.content import Content
#     # from db_models.file import File
#     # from db_models.named_entity import NamedEntity, EntityType
#     # from db_models.content_category import ContentCategory
#     # from db_models.content_entity import ContentEntity
#     # from db_models.element import Element
#     # from db_models.template import Template
#     db.init_app(app)
#     return db
    

def create_tables():
    db.create_all()

def drop_tables():
    db.drop_all()

def test_data_db():
    # create categories table 
    from db_models.category import Category
    db.create_all()
    db.session.add(Category('test'))
    db.session.commit()

    # retrieve data from db
    categories = Category.query.all()
    print(categories)