from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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