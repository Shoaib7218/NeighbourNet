import base64
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
from flask_socketio import send, join_room, leave_room
from extensions import socketio
from pymongo import MongoClient
from bson import ObjectId

search_user_tab_route = Blueprint('sur_page', __name__)

mongo_uri = "mongodb://localhost:27017/"
client = MongoClient(mongo_uri)

db = client['NeighbourNet']
community_collection = db['Communities']
user_collection = db['User_details']
message_collection = db['Messages_data']
event_collection = db['Events']
l_and_f_collections = db['report_l_and_f']
admin_request_collection = db['admin_requests']
user_request_collection = db['user_request']




@search_user_tab_route.route('/search-user-tab', methods=['POST', 'GET'])
def search_user_tab():
    query = request.form.get('query')
    community_id = request.form['community_id']
    results = user_collection.find(
        {'first_name': {'$regex': query.lower(), '$options': 'i'}},
        {'first_name': 1, 'last_name': 1, '_id': 1, 'profile_image': 1,'username':1}
    )
    results = list(results)
    for user in results:
        if user.get('profile_image'):
            user['profile_image'] = base64.b64encode(user['profile_image']).decode('utf-8')
    return render_template('search_user_tab.html', results=results, community_id=community_id, query=query)


@search_user_tab_route.route('/send-request-user,<community_id>,<requested_user>')
def send_request_user(community_id, requested_user):
    username = session['usermail']
    community_id = community_id
    requested_user = requested_user

    com_data = community_collection.find_one({'_id': ObjectId(community_id)})
    commo_name = com_data.get('community_name')
    commo_admin_name = com_data.get('admin_name')

    print(requested_user)

    # Check if the user is already in the community
    is_member = community_collection.find_one({'_id': ObjectId(community_id), 'users': requested_user})

    if is_member:
        return render_template('search_user_tab.html', message="User is already in the community")

    # Check if the request is already sent
    already_requested = user_request_collection.find_one({'community_id': community_id, 'username': requested_user})

    if already_requested:
        return render_template('search_user_tab.html', message="Request already sent")

    # Add the request if not already sent
    user_request_data = {
        "community_id": community_id,
        "username": requested_user,
        "commo_name": commo_name,
        "admin_name": commo_admin_name,
        "status": "pending"
    }

    user_request_collection.insert_one(user_request_data)

    return render_template('search_user_tab.html', message="Request sent successfully")






# @search_user_tab_route.route('/send-request-user,<community_id>,<requested_user>')
# def send_request_user(community_id,requested_user):
#
#     username = session['usermail']
#     community_id = community_id
#     requested_user = requested_user
#
#     com_data = community_collection.find_one({'_id':ObjectId(community_id)})
#
#     commo_name = com_data.get('community_name')
#     commo_admin_name = com_data.get('admin_name')
#
#     print(requested_user)
#
#     user_request_data = {
#         "community_id": community_id,
#         "username": requested_user,
#         "commo_name": commo_name,
#         "admin_name":commo_admin_name,
#         "status": "pending"
#     }
#
#     user_request_collection.insert_one(user_request_data)
#
#
#
#
#     return f"{requested_user}"
