from flask import Flask, render_template, request, redirect, url_for, Blueprint, session, flash
from login import login_routes
from pymongo import MongoClient # py mongo is a library while allows to interact with mongodb


#DataBase Connection To mongo

mongo_uri = "mongodb://localhost:27017/"   #Connection String
community_client = MongoClient(mongo_uri) #MongoClient is Class which helps us to establish connection with the data base

db = community_client['NeighbourNet'] # This access the DataBase if not it creates one
community_collection = db['Communities'] # To access the collection within the databases if not cretaes one
user_collections = db['User_details']

c_id = 0



#Creating routes

community_routes = Blueprint('community',__name__)  # we can import these routes int he main index file
form_data =[]

#Rendering to the Community file
@community_routes.route('/create-community')
def create_com():
    return render_template('commmunity.html')

@community_routes.route('/submit-community',methods=['POST',"GET"])
def community():

    if 'usermail' in session:

        username = session['usermail']
        user = user_collections.find_one({'username':username})


        if user:

            community_name = request.form['community_name']
            description = request.form['description']
            admin_name = user.get('first_name',user)
            location = request.form['location']
            privacy_type = request.form['privacy_type']
            community_rules = request.form['rules']
            event_prefeences = request.form['event_preferences']
            age_restriction = request.form['age_restrictions']
            emergency_contact = request.form['emergency_contact']

            if len(emergency_contact) != 10 or not emergency_contact.isdigit():
                flash("Emergency contact must be exactly 10 digits long", "warning")
                return redirect(url_for('community.create_com'))

            form_data.append(
                [community_name, community_rules, admin_name, description, location, privacy_type, event_prefeences,
                 age_restriction, emergency_contact])


            community_data = {
                "admin":username,
                "community_name": request.form['community_name'],
                "users" : [username,],
                "description": request.form['description'],
                "admin_name": admin_name,
                "location": request.form['location'],
                "privacy_type": request.form['privacy_type'],
                "community_rules": request.form['rules'],
                "event_preferences": request.form['event_preferences'],
                "age_restrictions": request.form['age_restrictions'],
                "emergency_contact": request.form['emergency_contact'],

            }



            #NOTE  : We have to perform all the crud operation


            result = community_collection.insert_one(community_data)
            _id = result.inserted_id #mongo db generates this unique id



            user_collections.update_one({'username': username},{'$push': {'communities': _id}})  # updating Data inside the User collection
                                       # this checks the username      This Update/adds the values

            return redirect(url_for('home.home_page'))

















