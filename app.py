from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_configuration import Base, Category, CategoryItem

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/categories')
def get_categories():
    categories = session.query(Category).all()
    output = ""
    for category in categories:
        output += "{id} - {name} <br/>".format(id=category.category_id, name=category.category_name)
    
    return output

@app.route('/categories')
@app.route('/categories/<category_id>')
def get_category():
    category = session.query(Category)

if __name__ == '__main':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)