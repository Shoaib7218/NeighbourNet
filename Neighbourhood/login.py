import threading, time
from flask import Flask, render_template, request, redirect, url_for, session, make_response, Blueprint, flash
from pymongo import MongoClient

mongo_uri = "mongodb://localhost:27017/"

login_client = MongoClient(mongo_uri)

db = login_client['NeighbourNet']

user_details_collection = db['User_details']

login_routes = Blueprint('login', __name__)

lock = threading.Lock()

# app = Flask(__name__)

# app.secret_key = "Shoaib's Key"



community_collection = db['Communities']
@login_routes.route('/')
def index():


     if 'usermail' in session: #usermail is a key in session and its value is username
        return redirect(url_for('login.home_page'))
     return render_template('login.html')


@login_routes.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if user_details_collection.find_one({'username': username}) and user_details_collection.find_one({'password':password}): #checking from db whether the login details are there or not
            session['usermail'] = username  #giving sessiona key value pair
            user = user_details_collection.find_one({'username':username})
            if user:
                fisrt_name = user.get('first_name',user)
            return redirect(url_for('login.home_page',username=fisrt_name))
        else:
            flash("Wrong Credentials",'success')
            return redirect(url_for('login.home_page'))

    response = make_response(render_template('login.html', username='', password=''))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response


@login_routes.route('/home')
def home_page():
    pass
    # if 'usermail' in session:  # checking for the key id session is created
    #     usermail = session.get('usermail') # fetching the name from the session go get the values only of the logged in user
    #     user = user_details_collection.find_one({'username':usermail}) # checking if the value usermail exists in the db or not
    #
    #     if user: # if yes
    #         #hello = "hi"
    #         first_name = user.get('first_name','user') #fetching from the user object passing the keyword "fisrt_name" e;se user
    #         return render_template('home.html',username=first_name) # rendering the first_name



    return redirect(url_for('login.index'))

# @login_routes.route('/home')
# def render_community_user_list():
#
#     if 'usermail' in session:
#         username = session['usermail']
#
#         # Find the user by username
#         user = user_details_collection.find_one({'username': username})
#
#         if user:


    # return "User not found or not logged in", 404


# @app.after_request
# def add_header(response):
#     response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0"
#     response.headers["Pragma"] = "no-cache"
#     response.headers["Expires"] = "0"
#     return response


# form_data = []
# @app.route('/submit-community',methods=['POST',"GET"])
# def community():
#     community_name = request.form['community_name']
#     description = request.form['description']
#     admin_name = request.form['admin_name']
#     location = request.form['location']
#     privacy_type = request.form['privacy_type']
#     community_rules = request.form['rules']
#     event_prefeences = request.form['event_preferences']
#     age_restriction = request.form['age_restrictions']
#     emergency_contact = request.form['emergency_contact']
#
#     form_data.append(
#         [community_name, community_rules, admin_name, description, location, privacy_type, event_prefeences,
#          age_restriction, emergency_contact])
#     print(form_data)
#     return f"DATA ADDED {community_name} {admin_name}"

# @login_routes.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login.index'))



