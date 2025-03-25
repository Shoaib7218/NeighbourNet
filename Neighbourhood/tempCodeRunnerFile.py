#SAS
from flask import Flask , render_template, request, redirect, url_for , Blueprint,session
from flask_socketio import SocketIO
import base64
app = Flask(__name__)

#passing our app in socket io

socketio =  SocketIO(app)

# App Configuration
app.secret_key = "Shoaib's Key"

# Import routes
from login import login_routes
from community import community_routes,form_data
from home import home_routes
from signup import signup_routes
from search_u_c import search_routes
from community_page import community_page_route



@app.template_filter('b64encode')
def b64encode_filter(data):
    if data is None:
        return ''
    return base64.b64encode(data).decode('utf-8')

# Register routes from the `login`
app.register_blueprint(home_routes)
app.register_blueprint(login_routes)
app.register_blueprint(community_routes)
app.register_blueprint(signup_routes)
app.register_blueprint(search_routes)
app.register_blueprint(community_page_route)
# app.register_blueprint(home_routes) # problem is giving priority to these routes the route to render home is also in login and as well as home

print(form_data)



if __name__ == "__main__":
    socketio.run(app)