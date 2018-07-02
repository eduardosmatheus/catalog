#!/usr/bin/python3
#encoding: utf-8
from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, joinedload
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from db_configuration import Base, Category, CategoryItem, User
import httplib2, random, string, json, requests

app = Flask(__name__)
app.secret_key = b'\x98z\xe5\xbb\xce\xba\x7f\x7f\x1bi?\x90\x96X7+'

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
# Base.metadata.drop_all()
Base.metadata.create_all(engine)

# Sessao do banco
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Token de acesso à API de login.
CLIENT_ID = json.loads(open('client-secrets.json', 'r').read())['web']['client_id']

# Home page
@app.route("/", methods=["GET"])
def home():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    data = session.query(Category).all()
    return render_template("categories.html", categories=data, state=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
        
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client-secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        return redirect(url_for('home'))

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = { 'access_token': credentials.access_token, 'alt': 'json' }
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(data['email'])

    if not user_id:
        createUser(login_session)

    login_session['user_id'] = user_id
    return redirect(url_for('getCategories'))

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token
    validateToken = httplib2.Http()
    result = json.loads(validateToken.request(url, 'GET')[1])
    
    if result.get('error') is None:
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
        h = httplib2.Http()
        result = h.request(url, 'GET', headers={'content-type': 'application/x-www-form-urlencoded'})[0]
        
        if result['status'] == '200':
            del login_session['access_token']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            return redirect(url_for('home'))
        else:
            response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response
    else:
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        return redirect(url_for('home'))

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/categories')
def getCategories():
    categories = session.query(Category).all()
    return render_template("categories.html", categories=categories)

@app.route('/categories/<int:id>')
def getCategory(id):
    category = session.query(Category).get(id)
    items = session.query(CategoryItem).filter(CategoryItem.category_id == id).all()
    return render_template("category.html", category=category, items=items)

@app.route("/categories/new", methods=["GET"])
def newCategory():
    return render_template("category_form.html", category=None)

@app.route("/categories/new", methods=["POST"])
def addNewCategory():
    try:
        currentUser = getUserID(login_session['email'])
        newCategory = Category(name = request.form["name"], user_id=currentUser)
        session.add(newCategory)
        session.commit()
    except:
        session.rollback()
    return redirect(url_for("home"))

@app.route("/categories/<int:id>/edit", methods=["GET", "POST"])
def updateCategory(id):
    currentCategory = session.query(Category).get(id)
    if request.method == "POST":
        try:
            currentCategory.name = request.form["name"]
            session.commit()
        except:
            session.rollback()
        return redirect(url_for("home"))
    else:
        return render_template("category_form.html", category=currentCategory)
    
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
    currentUser = getUserID(login_session['email'])
    newCategoryItem = CategoryItem(
        name = request.form["name"],
        details = request.form["details"],
        category_id=id,
        user_id=currentUser
    )
    try:
        session.add(newCategoryItem)
        session.commit()
    except:
        session.rollback()
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
    currentItem = session.query(CategoryItem).get(item_id)
    try:
        currentItem.name = request.form["name"]
        currentItem.details = request.form["details"]
        session.commit()
    except:
        session.rollback()
    return redirect(url_for("home"))

@app.route("/categories/<int:id>/items/<int:item_id>/delete")
def deleteCategoryItem(id, item_id):
    currentItem = session.query(CategoryItem).get(item_id)
    session.delete(currentItem)
    session.commit()
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)