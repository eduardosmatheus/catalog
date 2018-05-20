from flask import Flask, request, redirect, url_for, render_template
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, joinedload
from db_configuration import Base, Category, CategoryItem

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
# Base.metadata.drop_all()
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route("/", methods=["GET"])
def home():
    data = session.query(Category).all()
    return render_template("categories.html", categories=data)

@app.route('/categories/<int:id>')
def getCategory(id):
    category = session.query(Category).get(id)
    items = session.query(CategoryItem).filter(CategoryItem.category_id == id).all()
    return render_template("category.html", category=category, items=items)

@app.route("/categories/new", methods=["GET"])
def newCategory():
    return render_template("newcategory.html", category=None)

@app.route("/categories/new", methods=["POST"])
def addNewCategory():
    newCategory = Category(name = request.form["name"])
    session.add(newCategory)
    session.commit()
    return redirect(url_for("home"))

@app.route("/categories/<int:id>/edit", methods=["GET", "POST"])
def updateCategory(id):
    currentCategory = session.query(Category).get(id)
    if request.method == "POST":
        currentCategory.name = request.form["name"]
        session.commit()
        return redirect(url_for("home"))
    else:
        return render_template("category.html", category=currentCategory)
    
@app.route("/categories/<int:id>/delete")
def deleteCategory(id):
    currentCategory = session.query(Category).get(id)
    session.delete(currentCategory)
    session.commit()
    return redirect(url_for("home"))

@app.route("/categories/<int:id>/items/new")
def newCategoryItem(id):
    return render_template("newcategoryitem.html", id = id)

@app.route('/categories/<int:id>/items', methods=["POST"])
def addNewCategoryItem(id):
    newCategoryItem = CategoryItem(name = request.form["name"], details = request.form["details"], category_id=id)
    session.add(newCategoryItem)
    session.commit()
    return redirect(url_for("home"))

@app.route("/categories/<int:id>/items/<int:item_id>")
def getCategoryItem(id, item_id):
    item = session.query(CategoryItem).get(item_id)
    return render_template("category_item.html", item = item)

@app.route("/categories/<int:id>/items/<int:item_id>/edit", methods=["GET"])
def editCategoryItem(id, item_id):
    currentItem = session.query(CategoryItem).get(item_id)
    return render_template("editcategoryitem.html", item=currentItem)

@app.route("/categories/<int:id>/items/<int:item_id>/edit", methods=["POST"])
def updateCategoryItem(id, item_id):
    print("Chegueii")
    currentItem = session.query(CategoryItem).get(item_id)
    currentItem.name = request.form["name"]
    currentItem.details = request.form["details"]
    session.commit()
    return redirect(url_for("home"))

@app.route("/categories/<int:id>/items/<int:item_id>/delete")
def deleteCategoryItem(id, item_id):
    currentItem = session.query(CategoryItem).get(item_id)
    session.delete(currentItem)
    session.commit()
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)