#SAS

from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, make_response, Blueprint, Response,flash
from pymongo import MongoClient


# Connecting to the database
mongo_uri = "mongodb://localhost:27017/"
login_client = MongoClient(mongo_uri)
db = login_client['NeighbourNet']

user_collection = db['User_details']
community_collection = db['Communities']
admin_request_collection = db['admin_requests']
user_request_collection = db['user_request']
lost_and_found_collection = db['report_l_and_f']


# creating route
home_routes = Blueprint('home',__name__)


# rendreing the home page and its data
@home_routes.route('/home')
def render_home_page():

        if 'usermail' not in session:
            return redirect(url_for('login.index'))

        username = session['usermail']

        # Find the user by username
        user = user_collection.find_one({'username': username})

        if user:
            # displaying users First name on welcome Page
            first_name = user.get('first_name', 'user')
            username = user.get('username','Unknown')
            is_profile_image = user.get('profile_image',False)

            # displaying The communities in which user is or he has created
            c_ids = user.get('communities',[])

            c_ids = [ObjectId(cid) for cid in c_ids]

            user_communities = community_collection.find({'_id':{'$in':c_ids}}) # getting the whole collection


            # user_communities = community_collection.find({
            #     '$or': [
            #         {'_id': {'$in': c_ids}},  # Communities created by the user # this line can be used to diff admin
            #         {'users': username}  # Communities where the user is a member
            #     ]
            # })

            user_communities = list(user_communities)

            # user_data = community_collection.find({'_id': {'$in': c_ids}})
            #
            #user_community_name = [community.get('community_name','unnamed_community') for community in user_communities]# only retriving names


            # dilaying all the communities in explore community Section

            all_communitie = community_collection.find({},{'community_name':1,'description':1,'privacy_type':1,'_id':1,'users':1})

            all_communitie = list(all_communitie)

            for community in  all_communitie:
                community['is_member'] = username in community.get('users',[])

            already_requested = admin_request_collection.find_one({'username': username})

            already_requested_1 = False

            if already_requested:
                already_requested_1=True
            else:
                already_requested_1=False

            user_request_data = user_request_collection.find({},{'username':1,'commo_name':1,'community_id':1,'admin_name':1})

            the_user = []
            for doc in user_request_data:
                if username == doc['username']:
                    the_user.append(doc)


            user_data = user_collection.find_one({'username':username})
            # first_name = user_data.get('first_name')
            last_name = user_data.get('last_name')
            age = user_data.get('age')
            location = user.get('location')


            #  all_community = [com.get('community_name','unnamed community') for com in all_communitie] # only retriving names
            response = make_response(
                render_template('home.html', l1=user_communities, username=first_name, all_community=all_communitie,
                                user_name=username, already_requested=already_requested_1, the_user=the_user,
                                is_profile_image=is_profile_image,first_name=first_name,last_name=last_name,age=age,location=location))
            response.headers[
                'Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
            return response

            # return render_template('home.html',l1=user_communities,username=first_name,all_community=all_communitie,user_name=username,already_requested=already_requested_1,the_user=the_user,is_profile_image=is_profile_image)

        return "User not found or not logged in", 404



@home_routes.route('/profile-image')
def get_profile_image():
    # Retrieve the user document by username
    username = session['usermail']
    user = user_collection.find_one({'username': username})

    if user and 'profile_image' in user:
        # Serve the binary image as a response
        return Response(user['profile_image'], mimetype='image/jpeg')  # Adjust MIME type if needed  # do it again by yourself implementing your logic
    return "Image not found", 404



@home_routes.route('/request_add,<community_id>')
def add_user(community_id):

    username = session['usermail']

    community_id = community_id

    community_collection.update_one({'_id':ObjectId(community_id)},{'$push':{'users':username}})

    user_collection.update_one({'username':username},{'$push':{'communities':ObjectId(community_id)}})

    flash('You have been successfully added to the group', 'success')
    return redirect(url_for('home.render_home_page'))


@home_routes.route('/request,<community_id>')
def add_user_request(community_id):

    username = session['usermail']

    user_data = user_collection.find_one({'username':username})

    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')


    community_id = community_id

    request_data = {
        "community_id":community_id,
        "username":username,
        "first_name":first_name,
        "last_name":last_name,
        "status":"pending"
    }



    already_requested = admin_request_collection.find_one({'community_id':community_id,'username':username})

    # if already_requested:
    #     return "request sent already"
    # else:
    #     admin_request_collection.insert_one(request_data)
    #     return "request sent"
    if already_requested:
        flash('Request already sent', 'warning')
    else:
        admin_request_collection.insert_one(request_data)
        flash('Request sent successfully', 'success')

    return redirect(url_for('home.render_home_page'))  # Redirect to the desired page


# {
#     "_id": "some_id",
#     "community_id": "12345",
#     "user_email": "user@example.com",
#     "status": "pending" // or "approved" or "rejected"
# }




# @home_routes.route('/leave-group,<community_id>')
# def leave_group(community_id):
#
#     username = session['usermail']
#
#     user_collection.update_one({'username':username},{'$pull':{'communities':ObjectId(community_id)}})
#     community_collection.update_one({'_id':ObjectId(community_id)},{'$pull':{'users':username}})
#     flash('You have successfully left the group', 'success')
#     return redirect(url_for('home.render_home_page'))

@home_routes.route('/leave-group,<community_id>')
def leave_group(community_id):
    username = session['usermail']

    # Check if the user is the admin of the community
    community = community_collection.find_one({'_id': ObjectId(community_id)})
    if community and community.get('admin') == username:
        flash('You cannot leave the group because you are the admin. Please transfer admin rights before leaving.','warning')
        return redirect(url_for('home.render_home_page'))

    # Proceed with leaving the group if the user is not the admin
    user_collection.update_one({'username': username}, {'$pull': {'communities': ObjectId(community_id)}})
    community_collection.update_one({'_id': ObjectId(community_id)}, {'$pull': {'users': username}})
    lost_and_found_collection.update_one(
        {'community_id': community_id},
        {'$pull': {'reports': {'username': username}}}
    )

    flash('You have successfully left the group', 'success')
    return redirect(url_for('home.render_home_page'))


#shown in the request tab to the user
# @home_routes.route('/accept_como_request,<commo_id>')
# def accept_commo_request(commo_id):
#     commo_id = commo_id
#     username = session['usermail']
#
#     community_collection.update_one({'_id': ObjectId(commo_id)}, {'$push': {'users': username}})
#
#     user_collection.update_one({'username': username}, {'$push': {'communities': ObjectId(commo_id)}})
#
#     user_request_collection.delete_one({'username': username, 'community_id': commo_id})
#
#     return "you accepted the request"
#
# @home_routes.route('/reject_como_request,<commo_id>')
# def reject_commo_request(commo_id):
#     commo_id = commo_id
#     username = session['usermail']
#
#     # community_collection.update_one({'_id': ObjectId(commo_id)}, {'$push': {'users': username}})
#     #
#     # user_collection.update_one({'username': username}, {'$push': {'communities': ObjectId(commo_id)}})
#
#     user_request_collection.delete_one({'username':username,'community_id':commo_id})
#
#     return "you rejected the request"




@home_routes.route('/accept_como_request/<commo_id>')
def accept_commo_request(commo_id):
    username = session['usermail']

    community_collection.update_one({'_id': ObjectId(commo_id)}, {'$push': {'users': username}})
    user_collection.update_one({'username': username}, {'$push': {'communities': ObjectId(commo_id)}})
    user_request_collection.delete_one({'username': username, 'community_id': commo_id})

    flash('You accepted the request', 'success')
    return redirect(url_for('home.render_home_page'))  # Redirect to the home page or any other desired page

@home_routes.route('/reject_como_request/<commo_id>')
def reject_commo_request(commo_id):
    username = session['usermail']

    user_request_collection.delete_one({'username': username, 'community_id': commo_id})

    flash('You rejected the request', 'danger')
    return redirect(url_for('home.render_home_page'))  # Redirect to the home page or any other desired page

@home_routes.route('/logout', methods=['POST'])
def logout():
    session.clear()
    response = make_response(redirect(url_for('login.index')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response



@home_routes.route('/searches')
def redirect_search():
    return render_template('search_user_community.html')


@home_routes.route('/update_profile_image', methods=['POST'])
def update_profile_image():
    if 'profile_image' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('home.render_home_page'))

    file = request.files['profile_image']

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('home.render_home_page'))

    if file and allowed_file(file.filename):
        image_data = file.read()  # Read the image data

        # Update the user's profile image in the database
        user_collection.update_one(
            {'username': session['usermail']},
            {'$set': {'profile_image': image_data}}
        )

        flash('Profile image updated successfully', 'success')
        return redirect(url_for('home.render_home_page'))

    flash('Invalid file type', 'error')
    return redirect(url_for('home.render_home_page'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# @home_routes.route('/signout')
# def signout():
#     username = session['usermail']
#     admin_communities = community_collection.find({'admin': username})
#     admin_communities_count = community_collection.count_documents({'admin': username})
#     is_admin_of_multiple = admin_communities_count > 1
#     community_names = [community['community_name'] for community in admin_communities]
#     result_community_admins = {
#         'is_admin_of_multiple': is_admin_of_multiple,
#         'community_names': community_names
#     }
#     if is_admin_of_multiple:
#         flash(f'You are an admin of the following communities: {", ".join(community_names)}. Please transfer admin rights before signing out.','warning')
#         return redirect(url_for('home.render_home_page'))
#     # print(result_community_admins)
#     user_collection.delete_one({'username':username})
#     community_collection.update_many({'users':username},{'$pull':{'users':username}})
#     admin_request_collection.delete_one({'username':username})
#     user_request_collection.delete_one({'username':username})
#     lost_and_found_collection.update_many({'reports.username': username},{'$pull': {'reports': {'username': username}}})
#     session.clear()
#     response = make_response(redirect(url_for('login.index')))
#     response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
#     response.headers['Pragma'] = 'no-cache'
#     response.headers['Expires'] = '-1'
#     return response

@home_routes.route('/signout')
def signout():
    username = session.get('usermail')
    admin_communities = list(community_collection.find({'admin': username}, {'community_name': 1, '_id': 0}))

    if admin_communities:
        community_names = [community['community_name'] for community in admin_communities]
        flash(
            f'You are an admin of the following communities: {", ".join(community_names)}. Please transfer admin rights before signing out.',
            'warning'
        )
        return redirect(url_for('home.render_home_page'))

    user_collection.delete_one({'username': username})
    community_collection.update_many({'users': username}, {'$pull': {'users': username}})
    admin_request_collection.delete_one({'username': username})
    user_request_collection.delete_one({'username': username})
    lost_and_found_collection.update_many(
        {'reports.username': username},
        {'$pull': {'reports': {'username': username}}}
    )

    session.clear()
    response = make_response(redirect(url_for('login.index')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'

    return response

@home_routes.route('/remove-profile-picture-home')
def remove_profile_picture():
    username = session['usermail']
    user_collection.update_one({'username':username},{'$unset':{'profile_image':1}})
    flash('Profile picture removed successfully.', 'success')
    return redirect(url_for('home.render_home_page'))



@home_routes.route('/home')
def home_page():
    pass



# Logout route



















































#@home_routes.route('/home')
# def printhello():
#     if 'usermail' in session:  # checking for the key id session is created
#         usermail = session.get(
#             'usermail')  # fetching the name from the session go get the values only of the logged in user
#         user = user_collection.find_one(
#             {'username': usermail})  # checking if the value usermail exists in the db or not
#
#         if user:  # if yes
#             # hello = "hi"
#             first_name = user.get('first_name','user')  # fetching from the user object passing the keyword "fisrt_name" e;se user
#             return render_template('home.html', username=first_name)  # rendering the first_name
#     return render_template('home.html',hello="hi")



# l1 = [1,2,3]


