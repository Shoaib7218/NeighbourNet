#SAS
from flask import Flask , render_template, request, redirect, url_for , Blueprint,session
from extensions import socketio
from flask_cors import CORS
import base64
app = Flask(__name__)


app.secret_key = "Shoaib's Key"
CORS(app)
socketio.init_app(app,cors_allowed_origins="*")

# Import routes
from login import login_routes
from community import community_routes,form_data
from home import home_routes
from signup import signup_routes
from search_u_c import search_routes
from community_page import community_page_route
from view_events import view_events_route
from create_event import create_event_route
from lost_andf_ound import l_and_f_routes
from generate_report import gnr_routes
from search_user_tab import search_user_tab_route



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
app.register_blueprint(create_event_route)
app.register_blueprint(view_events_route)
app.register_blueprint(l_and_f_routes)
app.register_blueprint(gnr_routes)
app.register_blueprint(search_user_tab_route)
# app.register_blueprint(home_routes) # problem is giving priority to these routes the route to render home is also in login and as well as home

print(form_data)



if __name__ == "__main__":
    socketio.run(app,allow_unsafe_werkzeug=True)



# in the data passing usinf <a> if the data passed is not accurate then it will give url not found error