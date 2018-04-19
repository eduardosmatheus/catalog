from flask import Flask, request, redirect, url_for, render_template
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, lazyload
from db_configuration import Base, Category, CategoryItem

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route('/categories', methods=['GET'])
def getCategories():
    categories = session.query(Category).all()
    return render_template("categories.html", categories=categories)

@app.route('/categories/<int:category_id>')
def getCategory(category_id):
    category = session.query(Category).get(category_id).options(lazyload('children'))
    return render_template("category.html", category=category)

@app.route('/categories', methods=["POST"])
def addNewCategory():
    try:
        newCategory = Category(name = request.form["name"], items = [])
        session.add(newCategory)
        session.commit()
        return redirect("/categories", 200)
    except:
        session.rollback()
        return "Erro ao inserir uma categoria."

@app.route('/categories/<int:category_id>', methods=["PUT", "DELETE"])
def updateCategory(category_id):
    currentCategory = session.query(Category).get(category_id)

    if request.method == "PUT":
        currentCategory = Category(name = request.form["name"], items = request.form[""])
        session.commit()
        return "Categoria atualizada com sucesso!"
    else:
        session.delete(currentCategory)
        session.commit()
        return "Categoria removida com sucesso!"

if __name__ == '__main':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)