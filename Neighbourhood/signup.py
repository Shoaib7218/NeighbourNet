import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, render_template, request, redirect, url_for, session, make_response, Blueprint, flash
from pymongo import MongoClient
import re
import random

signup_routes = Blueprint('signup',__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client['NeighbourNet']
user_details_collection = db['User_details']

# @signup_routes.route('/signup',methods=['POST','GET'])
# def signup():
#     if request.method == 'POST':
#
#         first_name = request.form['first_name']
#         last_name= request.form['last_name']
#         username = request.form['username-email']
#         password = request.form['password']
#         age = request.form['age']
#         location = request.form['location']
#         communities = []
#         # profile_img = request.form['profile_image']
#         profile_img = request.files['profile_image'] # files requst for files in the form
#         password_match = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$_-/])[A-Za-z0-9@#$_-/]{8,}$'
#         # pas'sword_reg = re.
#         if user_details_collection.find_one({'username': username}):
#             return render_template('login.html',error="Username Already Exists")
#
#
#
#         if profile_img:
#             image_data = profile_img.read()
#             user_data = {
#                 "first_name": first_name,
#                 "last_name": last_name,
#                 "username": username,
#                 "password": password,
#                 "age": age,
#                 "location": location,
#                 "profile_image": image_data,
#                 "communities":communities
#             }
#             user_details_collection.insert_one(user_data)
#             return "user signed up successfully with profile image"
#         else:
#             user_data = {
#                 "first_name": first_name,
#                 "last_name": last_name,
#                 "username": username,
#                 "password": password,
#                 "age": age,
#                 "location": location,
#                 "communities": communities
#             }
#             user_details_collection.insert_one(user_data)
#             return "user signed up successfully without profile image"
#     return render_template('login.html')








# @signup_routes.route('/signup', methods=['POST'])
# def signup():
#     if request.method == 'POST':
#         first_name = request.form['first_name']
#         last_name = request.form['last_name']
#         username = request.form['username-email']
#         password = request.form['password']
#         age = request.form['age']
#         location = request.form['location']
#         communities = []
#         profile_img = request.files['profile_image']
#
#         password_match = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$_\-/])[A-Za-z0-9@#$_\-/]{8,}$'
#
#         # Check if the username already exists
#         if user_details_collection.find_one({'username': username}):
#             flash("Username already exists", "error")
#             return redirect(url_for('signup.signup', form_type='signup'))
#
#         # Check if the password meets the criteria
#         if not re.match(password_match, password):
#             flash("Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a digit, and a special character (@, #, $, _, -)", "error")
#             return redirect(url_for('signup.signup', form_type='signup'))
#
#         if profile_img:
#             image_data = profile_img.read()
#             user_data = {
#                 "first_name": first_name,
#                 "last_name": last_name,
#                 "username": username,
#                 "password": password,
#                 "age": age,
#                 "location": location,
#                 "profile_image": image_data,
#                 "communities": communities
#             }
#             send_email_notifications(username)
#             user_details_collection.insert_one(user_data)
#             flash("User signed up successfully with profile image", "success")
#         else:
#             user_data = {
#                 "first_name": first_name,
#                 "last_name": last_name,
#                 "username": username,
#                 "password": password,
#                 "age": age,
#                 "location": location,
#                 "communities": communities
#             }
#             send_email_notifications(username)
#             user_details_collection.insert_one(user_data)
#             flash("User signed up successfully without profile image", "success")
#
#         return redirect('/login')
#
#     return render_template('login.html', form_type='signup')
#
#
#
#
def generate_otp(length=4):
    digits = "0123456789"
    otp = ""
    for _ in range(length):
        otp += random.choice(digits)
    return otp
#
#
# def send_email_notifications(username):
#     from_my = 'shaikhshoaib7218@gmail.com'
#     password = 'vtvd jglz ppfj asgx'
#
#     username = username
#     # user_n = user_collection.find_one({'username':username})
#     # n = user_n.get('first_name')
#     # l = user_n.get('last_name')
#     # c_id = c_id
#
#     # email_cursor = community_collection.find_one({'_id': ObjectId(c_id)})
#     # email_addresses_of_users = email_cursor.get('users')
#     # adress = ['shaikhshoaib7218@gmail.com','shaikhafreen8421@gmail.com']
#
#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.starttls()
#     server.login(from_my, password)
#
#     msg = MIMEMultipart()
#     msg['From'] = from_my
#     msg['to'] = username
#     msg['Subject'] = f"OTP FOR SIGNUP"
#     msg.attach(MIMEText(f"A account on NeighbourNet has been created by this email {username}",
#                         'plain'))
#
#     server.send_message(msg)
#
#     server.quit()


@signup_routes.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username-email']
        password = request.form['password']
        age = request.form['age']
        location = request.form['location']
        communities = []
        profile_img = request.files['profile_image']

        password_match = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$_\-/])[A-Za-z0-9@#$_\-/]{8,}$'

        # Check if the username already exists
        if user_details_collection.find_one({'username': username}):
            flash("Username already exists", "error")
            return redirect(url_for('signup.signup', form_type='signup'))

        # Check if the password meets the criteria
        if not re.match(password_match, password):
            flash("Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a digit, and a special character (@, #, $, _, -)", "error")
            return redirect(url_for('signup.signup', form_type='signup'))



        otp = generate_otp()
        send_email_notifications(username, otp)

        if profile_img:
            image_data = profile_img.read()
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "password": password,
                "age": age,
                "location": location,
                "profile_image": image_data,
                "communities": communities,
                "otp": otp
            }
        else:
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "password": password,
                "age": age,
                "location": location,
                "communities": communities,
                "otp": otp
            }

        session['user_data'] = user_data
        flash("OTP sent to your email. Please verify.", "success")
        return redirect(url_for('signup.verify_otp'))

    return render_template('login.html', form_type='signup')


@signup_routes.route('/verify_otp', methods=['POST', 'GET'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form['otp']
        user_data = session.get('user_data')

        if user_data and user_data['otp'] == otp:
            user_data.pop('otp', None)  # Remove OTP before saving to the database
            user_details_collection.insert_one(user_data)
            session.pop('user_data', None)
            flash("OTP verified. Signup successful.", "success")
            return render_template('login.html', form_type="login")
        else:
            flash("Invalid OTP. Please try again.", "error")
            return redirect(url_for('signup.signup', form_type='signup'))

    return render_template('otp.html')



def send_email_notifications(username, otp):
    from_my = 'shaikhshoaib7218@gmail.com'
    password = 'vtvd jglz ppfj asgx'

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_my, password)

        msg = MIMEMultipart()
        msg['From'] = from_my
        msg['To'] = username
        msg['Subject'] = "OTP FOR SIGNUP"
        msg.attach(
            MIMEText(f"A account on NeighborNet has been created by this email {username}. Your OTP is {otp}", 'plain'))

        server.send_message(msg)
        server.quit()
    except Exception as e:
        flash("Email not found. Please check the email address and try again.", "error")
        return redirect(url_for('signup.signup'))



