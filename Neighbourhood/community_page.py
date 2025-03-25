# #SAS
# import threading, time
#
#
# from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
# from flask_socketio import send, join_room, leave_room
# from pymongo import MongoClient
# from bson import ObjectId
# from extensions import socketio
#
#
# # from NeighbourHood_Community.index import socketio
#
# community_page_route = Blueprint('c_page',__name__)
#
#
#
# mongo_uri = "mongodb://localhost:27017/"
#
# client = MongoClient(mongo_uri)
#
# db = client['NeighbourNet']
#
# community_collection = db['Communities'] #this is the problem why i wasted my 2 hours a spelling mistake
# user_collection = db['User_details']
#
# #dict for displaying messages
# messages = {}
#
# @community_page_route.route('/community/<community_n>')
# def render_page(community_n):
#     community = community_collection.find_one({'_id': ObjectId(community_n)})
#
#     c_name = community.get('community_name','Unnamed')
#     c_id = community.get('_id')
#     c_id = ObjectId(c_id)
#
#     print("Community:", community)
#
#     if community:
#         members = community.get('users', [])
#     else:
#         members = []
#
#     print("Members:", members)
#
#
#     names = user_collection.find({'username':{'$in':members}})
#
#     name1 = [name.get('first_name','unknown')+" "+ name.get('last_name') for name in names]
#     print(name1)
#
#     community_messages = messages.get(str(c_id),[])
#     print("Messages for community:", community_messages)
#     return render_template('community_page.html', community_name=c_name, members=name1,  community_id=str(c_id),messages=community_messages)
#
# @socketio.on('join')
# def on_join(data):
#     username = data['username']
#     room = data['room']
#     join_room(room)
#     send(f"{username} has entered the room.", to=room)
#
# @socketio.on('leave')
# def on_leave(data):
#     username = data['username']
#     room = data['room']
#     leave_room(room)
#     send(f"{username} has left the room.", to=room)
#
# @socketio.on('message')
# def on_message(data):
#     room = data['room']
#     message = f'{data["username"]}: {data["message"]}'
#     if room not in messages:
#         messages[room] = []
#     messages[room].append(message)
#     send(message, to=room)
import base64
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, Blueprint,flash
from flask_socketio import send, join_room, leave_room
from extensions import socketio
from pymongo import MongoClient
from bson import ObjectId

community_page_route = Blueprint('c_page', __name__)

mongo_uri = "mongodb://localhost:27017/"
client = MongoClient(mongo_uri)

db = client['NeighbourNet']
community_collection = db['Communities']
user_collection = db['User_details']
message_collection = db['Messages_data']
event_collection = db['Events']
l_and_f_collections = db['report_l_and_f']
admin_request_collection = db['admin_requests']

# dict for displaying messages
messages = {}

@community_page_route.route('/community/<community_n>/<username>')
def render_page(community_n,username):
    community = community_collection.find_one({'_id': ObjectId(community_n)})
    c_name = community.get('community_name', 'Unnamed')
    c_id = str(community.get('_id'))



    # if community:
    #     members = community.get('users', [])
    # else:
    #     members = []
    #
    # names = user_collection.find({'username': {'$in': members}})
    # name1 = [name.get('first_name', 'unknown') + " " + name.get('last_name', '') for name in names]
    #
    # user_name = username
    # print(user_name)

    if community:
        members = community.get('users', [])
    else:
        members = []

    names = user_collection.find({'username': {'$in': members}}, {'first_name': 1, 'last_name': 1, 'username': 1})
    name_details = [{'first_name': name.get('first_name', 'unknown'), 'last_name': name.get('last_name', ''),
                     'username': name.get('username', '')} for name in names]

    user_name = username
    print(user_name)

    first_ = user_collection.find_one({'username':user_name})
    if first_:
        first_name = first_.get('first_name', "NoNe")
    else:
        first_name = "NoNe"
    print(first_name)



    community_messages = messages.get(c_id, [])
    print("Messages for community:", community_messages)

    requests = admin_request_collection.find({'community_id': c_id})

    is_admin_1 = community.get('admin') == username
    admin_username = community.get('admin')


    return render_template('community_page.html', community_name=c_name, members=name_details, community_id=c_id, messages=community_messages,user = user_name,first_=first_name,is_admin=is_admin_1,requests=requests,admin_username=admin_username)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']  # This represents the community
    join_room(room)
    send(f"{username} has entered the community's Chatroom.", to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(f"{username} has left the community's Chatroo.", to=room)

@socketio.on('message')
def on_message(data):
    community = data['room']
    username = data['username']
    message = data['message']

    # Ensure messages dictionary is initialized for the community
    if community not in messages:
        messages[community] = []

    # fetching the communities in message collection to check whether it already exists or not



    message_c_id_data = message_collection.find_one({'community_id':data['room']})

    if message_c_id_data:
        message_collection.update_one({'community_id':data['room']},{'$push':{'chats':{data['username']:data['message']}}})
    else:
        data1 = {
            'community_id': data['room'],
            'chats': [{data['username']: data['message']}]

        }

        message_collection.insert_one(data1)


    # Append the new message for the community
    messages[community].append(f'{username}: {message}')


    # Broadcast the message to the room (community)
    send(f'{username}: {message}', to=community)


@community_page_route.route('/view_events/<community_id>')
def render_view_comm(community_id):
    # print(community_id)
    # return render_template('view_events.html',c_id=community_id)
    event_data = event_collection.find_one({'c_id': community_id})

    if event_data:
        print("hello")
    else:
        print("hi")

    data = event_data.get('data', []) if event_data else [] # my logic

    for i in data:
        for j, k in i.items():
            print(j, k)

    # print(event_data)

    return render_template('view_events.html', commo_id=community_id, data=data)


# @community_page_route.route('/lost-and-found,<community_id>')
# def render_l_and_f(community_id):
#     username = session['usermail']
#     print(community_id)
#     report = ['a', 'b']
#
#     print(community_id)
#     print(report)
#     report_lists = []
#     user_report_lists = []
#     # lf_docs = l_and_f_collections.find(
#     #     {'community': community_id},
#     #     {'reports.community_reports': 1,'reports.username':1, '_id': 0}
#     # )
#     # # print(report_lists)
#     # for doc in lf_docs:
#     #     for report in doc['reports']:
#     #         for c_report in report['community_reports']:
#     #             if c_report.get('item_image'):
#     #                 c_report['item_image'] = base64.b64encode(c_report['item_image']).decode('utf-8')
#     #             report_lists.append(c_report)
#     # print(report_lists)
#
#     # Perform the MongoDB query
#     lf_docs = l_and_f_collections.find(
#         {'community': community_id},
#         {'reports.community_reports': 1, 'reports.username': 1, '_id': 0}
#     )
#
#
#     report_lists = []
#     for doc in lf_docs:
#         for report in doc['reports']:
#             username = report.get('username')
#             for c_report in report['community_reports']:
#                 if c_report.get('item_image'):
#                     c_report['item_image'] = base64.b64encode(c_report['item_image']).decode('utf-8')
#                 c_report['username'] = username
#                 report_lists.append(c_report)
#
#
#     # print(report_lists)
#
#     # lf_users_only_doc = l_and_f_collections.find({'community':community_id,'reports.username':username}
#     #                                              ,{'reports.username':1,'reports.community_reports':1,'_id':0})
#     # for doc in lf_users_only_doc:
#     #     for report in doc['reports']:
#     #         if report['username']== username:
#     #             for user_reports in report['community_reports']:
#     #                 if user_reports.get('item_image'):
#     #                     user_reports['item_image'] = base64.b64encode(user_reports['item_image']).decode('utf-8')
#     #                 user_report_lists.append((user_reports))
#
#     # Perform the MongoDB query
#     lf_users_only_doc = l_and_f_collections.find(
#         {'community': community_id, 'reports.username': username},
#         {'reports.username': 1, 'reports.community_reports': 1, '_id': 1}  # Include _id in the query projection
#     )
#
#
#     user_report_lists = []
#     for doc in lf_users_only_doc:
#         for report in doc['reports']:
#             if report['username'] == username:
#                 for user_reports in report['community_reports']:
#                     if user_reports.get('item_image'):
#                         user_reports['item_image'] = base64.b64encode(user_reports['item_image']).decode('utf-8')
#                     user_reports['_id'] = doc['_id']
#                     user_report_lists.append(user_reports)
#
#     # Print the user_report_lists
#     # print(user_report_lists)
#
#     # print(user_report_lists)
#     return render_template('lost_and_found.html',community_id=community_id,reports = report_lists,user_reports=user_report_lists)
@community_page_route.route('/lost-and-found,<community_id>')
def render_l_and_f(community_id):
    username = session.get('usermail', 'default_username')  # Default value for debugging
    print(f"Community ID: {community_id}")
    print(f"Username: {username}")

    report_lists = []
    user_report_lists = []

    lf_docs = l_and_f_collections.find(
        {'community': community_id},
        {'reports.community_reports': 1, 'reports.username': 1, '_id': 0}
    )

    for doc in lf_docs:
        for report in doc['reports']:
            username = report.get('username')
            for c_report in report['community_reports']:
                if c_report.get('item_image'):
                    c_report['item_image'] = base64.b64encode(c_report['item_image']).decode('utf-8')
                c_report['username'] = username
                report_lists.append(c_report)

    lf_users_only_doc = l_and_f_collections.find(
        {'community': community_id, 'reports.username': username},
        {'reports.username': 1, 'reports.community_reports': 1, '_id': 1}
    )

    for doc in lf_users_only_doc:
        for report in doc['reports']:
            if report['username'] == username:
                for user_reports in report['community_reports']:
                    if user_reports.get('item_image'):
                        user_reports['item_image'] = base64.b64encode(user_reports['item_image']).decode('utf-8')
                    user_reports['_id'] = doc['_id']
                    user_report_lists.append(user_reports)

    print(f"Report Lists: {report_lists}")
    print(f"User Report Lists: {user_report_lists}")

    return render_template('lost_and_found.html', community_id=community_id, reports=report_lists,
                           user_reports=user_report_lists)


# @community_page_route.route('/accept-request-admin,<community_id>,<request_username>')
# def accept_request_admin(community_id,request_username):
#     print(community_id)
#     community_id=community_id
#     request_username = request_username
#
#     # admin_request_collection.find_one({})
#
#     community_collection.update_one({'_id':ObjectId(community_id)},{'$push':{'users':request_username}})
#     user_collection.update_one({'username':request_username},{'$push':{'communities':ObjectId(community_id)}})
#
#
#
#     admin_request_collection.delete_one({'community_id':community_id,'username':request_username})
#
#     return "accepted"

@community_page_route.route('/accept-request-admin/<community_id>/<request_username>')
def accept_request_admin(community_id, request_username):
    community = community_collection.find_one({'_id': ObjectId(community_id)})
    user_is_member = request_username in community.get('users', [])
    request_exists = admin_request_collection.find_one({'community_id': community_id, 'username': request_username})

    if user_is_member:
        flash('User is already a member of the group', 'warning')
    elif not request_exists:
        flash('No pending request found for this user', 'warning')
    else:
        community_collection.update_one({'_id': ObjectId(community_id)}, {'$push': {'users': request_username}})
        user_collection.update_one({'username': request_username}, {'$push': {'communities': ObjectId(community_id)}})
        admin_request_collection.delete_one({'community_id': community_id, 'username': request_username})
        flash('Request accepted successfully', 'success')

    return redirect(url_for('c_page.render_page', community_n=community_id, username=session['usermail'], _anchor='requests-tab'))




@community_page_route.route('/reject-request-admin,<community_id>,<request_username>')
def reject_request_admin(community_id,request_username):
    print(community_id)
    community_id=community_id
    request_username = request_username

    # admin_request_collection.find_one({})

    # community_collection.update_one({'_id':ObjectId(community_id)},{'$push':{'users':request_username}})
    # user_collection.update_one({'username':request_username},{'$push':{'communities':ObjectId(community_id)}})



    admin_request_collection.delete_one({'community_id':community_id,'username':request_username})

    return "rejected"

@community_page_route.route('/search_users/<community_id>', methods=['POST'])
def search_users(community_id):
    query = request.form.get('query')
    results = user_collection.find(
        {'first_name': {'$regex': query.lower(), '$options': 'i'}},
        {'first_name': 1, 'last_name': 1, '_id': 1, 'profile_image': 1}
    )
    results = list(results)
    return render_template('community_page.html', results=results, community_id=community_id)

@community_page_route.route('/go-to-search,<community_id>')
def go_to_search(community_id):
    community_id=community_id
    return render_template('search_user_tab.html',community_id=community_id)


@community_page_route.route('/make-admin,<new_admin_username>,<community_id>')
def make_admin(new_admin_username,community_id):

    username = session['usermail']
    community_collection.update_one({'_id':ObjectId(community_id),'admin':username},{'$set':{'admin':new_admin_username}})

    return redirect(url_for('c_page.render_page',community_n=community_id, username=username))



@community_page_route.route('/remove_user_by_admin,<member_username>,<community_id>')
def remove_user_by_admin(member_username,community_id):
    print(member_username)

    username = session['usermail']
    community_collection.update_one({'_id':ObjectId(community_id),'users':member_username},{'$pull':{'users':member_username}})
    user_collection.update_one( {'username': member_username, 'communities': ObjectId(community_id)}, {'$pull': {'communities': ObjectId(community_id)}} )

    return redirect(url_for('c_page.render_page',community_n=community_id, username=username))


@community_page_route.route('/leave_group/<community_id>')
def leave_group(community_id):
    username = session['usermail']
    community = community_collection.find_one({'_id': ObjectId(community_id)})
    is_admin = community.get('admin') == username

    if is_admin:
        # Check if there are other members to appoint as admin
        members = community.get('users', [])
        if len(members) > 1:
            flash('You need to appoint another user as an admin before leaving the group', 'warning')
            return redirect(url_for('c_page.render_page', community_n=community_id, username=username, _anchor='requests-tab'))
        else:
            flash('You cannot leave the group as you are the only member', 'warning')
            return redirect(url_for('c_page.render_page', community_n=community_id, username=username, _anchor='requests-tab'))
    else:
        # Remove user from community and user's communities list
        user_collection.update_one({'username': username}, {'$pull': {'communities': ObjectId(community_id)}})
        community_collection.update_one({'_id': ObjectId(community_id)}, {'$pull': {'users': username}})

        flash('You have successfully left the group', 'success')
        return redirect(url_for('home.render_home_page'))




@community_page_route.route('/delete_community/<community_id>')
def delete_community(community_id):
    username = session['usermail']
    community = community_collection.find_one({'_id': ObjectId(community_id)})


    if community.get('admin') == username:

        user_collection.update_many(
            {'communities': ObjectId(community_id)},
            {'$pull': {'communities': ObjectId(community_id)}}
        )


        community_collection.delete_one({'_id': ObjectId(community_id),'admin':username})


        admin_request_collection.delete_many({'community_id': community_id})

        flash('Community has been successfully deleted', 'success')
        return redirect(url_for('home.render_home_page'))
    else:
        flash('Only the admin can delete this community', 'warning')
        return redirect(url_for('c_page.render_page', community_n=community_id, username=username))




# @community_page_route.route('#addusers-content,<community_id>')
# def request_admin_users(community_id):
#
#     username = session['usermail']
#     community_id = community_id
#
#     requests = admin_request_collection.find({'community_id':community_id})
#
#     return



