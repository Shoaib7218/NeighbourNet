from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, make_response, Blueprint, Response,flash
from pymongo import MongoClient


search_routes = Blueprint('search',__name__)


mongo_uri = "mongodb://localhost:27017/"

client = MongoClient(mongo_uri)

db = client['NeighbourNet']

user_collection = db['User_details']

community_collection = db['Communities']
admin_request_collection = db['admin_requests']



@search_routes.route('/search',methods = ['POST','GET'])
def search_():

    results = []

    query = None

    if request.method == 'POST':

        query = request.form.get('query')

        results = user_collection.find({'first_name':{'$regex':query.lower(),'$options':'i'}},{'first_name':1,'last_name':1,'_id':1,'profile_image':1})

        results = list(results)

    return render_template('search_user_tab.html',result = results, query = query)


# @search_routes.route('/search_community',methods=['POST','GET'])
# def search_c():
#     results = []
#     query1 = None
#     if request.method == 'POST':
#
#         query1 = request.form.get('query-c')
#
#         results = community_collection.find({'community_name':{'$regex':query1.lower(),'$options':'i'}},{'community_name':1,'_id':1,'privacy_type':1})
#
#     return render_template('search_user_community.html',result1=results,query1=query1)

@search_routes.route('/search_community', methods=['POST', 'GET'])
def search_c():
    results = []
    query1 = None
    if request.method == 'POST':
        query1 = request.form.get('query-c')
        results = list(community_collection.find({'community_name': {'$regex': query1, '$options': 'i'}}, {'community_name': 1, 'privacy_type': 1, 'description':1}))

    username = session['usermail']
    user_data = user_collection.find_one({'username': username})
    user_communities = user_data.get('communities', [])
    requested_communities = admin_request_collection.find({'username': username})
    requested_community_ids = [req['community_id'] for req in requested_communities]

    return render_template('search_user_community.html', result1=results, query1=query1, user_communities=user_communities, requested_community_ids=requested_community_ids)



# @search_routes.route('/request/<community_id>')
# def search_for_comm_in_s_u_c(community_id):
#     username = session['usermail']
#     user_data = user_collection.find_one({'username': username})
#
#     first_name = user_data.get('first_name')
#     last_name = user_data.get('last_name')
#
#     request_data = {
#         "community_id": community_id,
#         "username": username,
#         "first_name": first_name,
#         "last_name": last_name,
#         "status": "pending"
#     }
#
#     already_requested = admin_request_collection.find_one({'username': username, 'community_id': community_id})
#
#     if already_requested:
#         flash('Request already sent', 'warning')
#     else:
#         admin_request_collection.insert_one(request_data)
#         flash('Request sent successfully', 'success')
#
#     return redirect(url_for('search.search_c'))  # Redirect to the same search page


@search_routes.route('/request/<community_id>', methods=['POST'])
def search_for_comm_in_s_u_c(community_id):
    username = session['usermail']
    user_data = user_collection.find_one({'username': username})

    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')

    request_data = {
        "community_id": community_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "status": "pending"
    }

    already_requested = admin_request_collection.find_one({'username': username, 'community_id': community_id})

    if already_requested:
        flash('Request already sent', 'warning')
    else:
        admin_request_collection.insert_one(request_data)
        flash('Request sent successfully', 'success')

    return redirect(url_for('search_routes.search_c'))  # Redirect to the same search page




# @search_routes.route('/profile/<_id>')
# def get_profile_image(user_id):
#     username = session['usermail']
#
#     user = user_collection.find_one({'_id':ObjectId(user_id)})
#
#     if user and 'profile_image' in user:
#
#         return Response(user['profile_image'],mimetype='image/jpeg')
#     return "image not found"







