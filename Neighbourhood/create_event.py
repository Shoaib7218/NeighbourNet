from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, make_response, Blueprint, Response
from pymongo import MongoClient
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


create_event_route = Blueprint('c_e_r','__name__')

mongo_uri = "mongodb://localhost:27017/"

client = MongoClient(mongo_uri)

db = client['NeighbourNet']
event_collection = db['Events']
communtiy_collection = db['Communities']
user_collection = db['User_details']

@create_event_route.route('/create_event1',methods=['POST','GET'])
def add_data():

    username= session['usermail']

    user_n = user_collection.find_one({'username':username})
    name = user_n.get('first_name')
    last = user_n.get('last_name')
    if request.method == "POST":

        title = request.form['event-title']
        description = request.form['event-descrp']
        date = request.form['event-date']
        time = request.form['event-time']
        c_id = request.form['community_id']

        event = event_collection.find_one({'c_id':c_id})
        if event:
            event_collection.update_one({'c_id':c_id},{'$push':{'data':{'title': title, 'description': description, 'date': date, 'time': time}}})
        else:
            data = {
                'c_id': c_id,
                'data': [{'title': title, 'description': description, 'date': date, 'time': time}]
            }

            event_collection.insert_one(data)
        com_data = communtiy_collection.find_one(ObjectId(c_id))

        print(com_data.get('community_name'))
        print(title,date,description,time,c_id)

        from_my = 'shaikhshoaib7218@gmail.com'
        password = 'vtvd jglz ppfj asgx'

        email_cursor = communtiy_collection.find_one({'_id':ObjectId(c_id)})
        email_addresses_of_users = email_cursor.get('users')
        # email_addresses_of_users = [email.get('users') for email in email_cursor] # i wanted only one community and i used find insted of find_one
        print(email_addresses_of_users)
        adress = ['shaikhshoaib7218@gmail.com','shaikhafreen8421@gmail.com']


        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_my, password)

        for e in adress:
            msg = MIMEMultipart()
            msg['From'] = from_my
            msg['to'] = e
            msg['Subject'] = f"An Event Has Created By the {name} {last} from {com_data.get('community_name')}"
            msg.attach(MIMEText(f"TITLE : {title} \n DESCRIPTION : {description}\n DATE : {date} \n TIME: {time} \n FROM {com_data.get('community_name')}",'Plain'))


            server.send_message(msg)
        server.quit()
        return redirect(url_for('c_page.render_view_comm',community_id=c_id)) # you should always return something
            # Send the email
