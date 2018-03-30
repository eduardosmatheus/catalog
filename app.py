from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_configuration import Base, Category, CategoryItem

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)

@app.route('/')
@app.route('/hello')
def HelloWorld():
    return "Hello world"

if __name__ == '__main':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)