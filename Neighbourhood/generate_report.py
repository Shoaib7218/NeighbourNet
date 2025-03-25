from datetime import datetime

from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, make_response, Blueprint, Response,flash
from pymongo import MongoClient
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

gnr_routes = Blueprint('gnrs',__name__)


mongo_uri = "mongodb://localhost:27017/mydatabase"

client = MongoClient(mongo_uri)

db = client['NeighbourNet']

l_and_f_collections = db['report_l_and_f']

community_collection = db['Communities']

user_collection = db['User_details']








@gnr_routes.route('/submit-report', methods=['POST', 'GET'])
def add_data():
    if request.method == 'POST':
        item_name = request.form['item-name']
        item_description = request.form['item-description']
        item_image = request.files['item-image']
        lost_location = request.form['location']
        contact_p = request.form['contact']
        community_id = request.form['community_id']
        username = session['usermail']
        print(community_id)

        lf_check = l_and_f_collections.find_one({'community': community_id})

        if lf_check:
            lf_check_community = lf_check.get('community')
            if lf_check_community:
                user_found = False
                for report in lf_check['reports']:
                    if report['username'] == username:
                        user_found = True
                        break
                if user_found:
                    if item_image:
                        image_data = item_image.read() if item_image else None
                        data = {
                            "item_name": item_name,
                            "item_description": item_description,
                            "item_image": image_data,
                            "lost_location": lost_location,
                            "contact_p": contact_p
                        }
                        l_and_f_collections.update_one({'community': community_id, 'reports.username': username},
                                                       {'$push': {'reports.$.community_reports': data}})
                        send_email_notifications(community_id, item_name, item_description)
                        flash('Data submitted and email notifications sent', 'success')
                        return redirect(url_for('c_page.render_l_and_f', community_id=community_id))
                    else:
                        data = {
                            "item_name": item_name,
                            "item_description": item_description,
                            "lost_location": lost_location,
                            "contact_p": contact_p
                        }
                        l_and_f_collections.update_one({'community': community_id, 'reports.username': username},
                                                       {'$push': {'reports.$.community_reports': data}})
                        send_email_notifications(community_id, item_name, item_description)
                        flash('Data submitted and email notifications sent', 'success')
                        return redirect(url_for('c_page.render_l_and_f', community_id=community_id))
                else:
                    if item_image:
                        image_data = item_image.read()
                        data = {
                            "username": username,
                            "community_reports": [{
                                "item_name": item_name,
                                "item_description": item_description,
                                "item_image": image_data,
                                "lost_location": lost_location,
                                "contact_p": contact_p
                            }]
                        }
                        l_and_f_collections.update_one({'community': community_id}, {'$push': {'reports': data}})
                        send_email_notifications(community_id, item_name, item_description)
                        flash('Data submitted and email notifications sent', 'success')
                        return redirect(url_for('c_page.render_l_and_f', community_id=community_id))
                    else:
                        data = {
                            "username": username,
                            "community_reports": [{
                                "item_name": item_name,
                                "item_description": item_description,
                                "lost_location": lost_location,
                                "contact_p": contact_p
                            }]
                        }
                        l_and_f_collections.update_one({'community': community_id}, {'$push': {'reports': data}})
                        send_email_notifications(community_id, item_name, item_description)
                        flash('Data submitted and email notifications sent', 'success')
                        return redirect(url_for('c_page.render_l_and_f', community_id=community_id))
        else:
            if item_image:
                image_data = item_image.read()
                data = {
                    "community": community_id,
                    "reports": [{
                        "username": username,
                        "community_reports": [{
                            "item_name": item_name,
                            "item_description": item_description,
                            "item_image": image_data,
                            "lost_location": lost_location,
                            "contact_p": contact_p
                        }]
                    }]
                }
                l_and_f_collections.insert_one(data)
                send_email_notifications(community_id, item_name, item_description)
                flash('Data submitted and email notifications sent', 'success')
                return redirect(url_for('c_page.render_l_and_f', community_id=community_id))
            else:
                data = {
                    "community": community_id,
                    "reports": [{
                        "username": username,
                        "community_reports": [{
                            "item_name": item_name,
                            "item_description": item_description,
                            "lost_location": lost_location,
                            "contact_p": contact_p
                        }]
                    }]
                }
                l_and_f_collections.insert_one(data)
                send_email_notifications(community_id, item_name, item_description)
                flash('Data submitted and email notifications sent', 'success')
                return redirect(url_for('c_page.render_l_and_f', community_id=community_id))

# @gnr_routes.route('/submit-report', methods=['POST', 'GET'])
# def add_data():
#     if request.method == 'POST':
#         item_name = request.form['item-name']
#         item_description = request.form['item-description']
#         item_image = request.files['item-image']
#         lost_location = request.form['location']
#         contact_p = request.form['contact']
#         community_id = request.form['community_id']
#         username = session['usermail']
#
#         # Read image data if provided
#         image_data = item_image.read() if item_image else None
#
#         # Create the report object
#         report_data = {
#             "item_name": item_name,
#             "item_description": item_description,
#             "item_image": image_data,
#             "lost_location": lost_location,
#             "contact_p": contact_p,
#             "created_at": datetime.utcnow()  # Timestamp for the report
#         }
#
#         # Check if the community exists
#         community = l_and_f_collections.find_one({"_id": community_id})
#
#         if community:
#             # Check if the user exists in the community
#             user_found = any(user['username'] == username for user in community['users'])
#
#             if user_found:
#                 # Add the report to the user's reports
#                 l_and_f_collections.update_one(
#                     {"_id": community_id, "users.username": username},
#                     {"$push": {"users.$.reports": report_data}}
#                 )
#             else:
#                 # Add a new user with their first report
#                 new_user = {
#                     "username": username,
#                     "reports": [report_data]
#                 }
#                 l_and_f_collections.update_one(
#                     {"_id": community_id},
#                     {"$push": {"users": new_user}}
#                 )
#         else:
#             # Create a new community document with the user and their report
#             new_community = {
#                 "_id": community_id,
#                 "community_name": "Community Name",  # Replace with actual name if available
#                 "users": [
#                     {
#                         "username": username,
#                         "reports": [report_data]
#                     }
#                 ]
#             }
#             l_and_f_collections.insert_one(new_community)
#
#         # Send email notifications
#         send_email_notifications(community_id, item_name, item_description)
#         flash('Data submitted and email notifications sent', 'success')
#         return redirect(url_for('c_page.render_l_and_f', community_id=community_id))
#


def send_email_notifications(c_id, title, description):
    from_my = 'shaikhshoaib7218@gmail.com'
    password = 'vtvd jglz ppfj asgx'

    username = session['usermail']
    user_n = user_collection.find_one({'username':username})
    n = user_n.get('first_name')
    l = user_n.get('last_name')
    c_id = c_id

    email_cursor = community_collection.find_one({'_id': ObjectId(c_id)})
    # email_addresses_of_users = email_cursor.get('users')
    adress = ['shaikhshoaib7218@gmail.com','shaikhafreen8421@gmail.com']

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_my, password)

    for e in adress:
        msg = MIMEMultipart()
        msg['From'] = from_my
        msg['to'] = e
        msg['Subject'] = f"New Lost & Found Report in {email_cursor.get('community_name')} by {n} {l}"
        msg.attach(MIMEText(f"TITLE: {title}\nDESCRIPTION: {description}\nCOMMUNITY: {email_cursor.get('community_name')}", 'plain'))

        server.send_message(msg)
    server.quit()









                    # reports.$.community_reports the $ is a positional operator which is used to match the specific community as there will be multiple community
                    # for more understanding the doc in mongodb

                    # for data to search in the nested we have to use loop or if there is a nested document then we have to call it by the parent doc

                    # for eg : for the loop one if its a list doc we have to check it using a list
                    # for i in collection['item']:
                    #       if i == j:
                              # reutrn True

                    # and for nested search in the update function we have to call its parent for eg
                # l_and_f_collections.update_one({'community': community_id, 'reports.username': username},
                                               # {'$push': {'reports.$.community_reports': data}})













