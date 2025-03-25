# import base64
#
# from bson import ObjectId
# from flask import Flask, render_template, request, redirect, url_for, session, make_response, Blueprint, Response
# from pymongo import MongoClient
#
# l_and_f_routes = Blueprint('l_and_f',__name__)
#
# mongo_uri = "mongodb://localhost:27017/mydatabase"
#
# client = MongoClient(mongo_uri)
#
# db = client['NeighbourNet']
#
# l_and_f_collections = db['report_l_and_and_f']
#
#
# @l_and_f_routes.route('/generate_report,<community_id>',methods=['POST','GET'])
# def red_g_report(community_id):
#     print(community_id)
#     report_lists = []
#     lf_doc = l_and_f_collections.find({'community':community_id},{'reports.community_reports':1,'_id':0})
#
#     for reports in lf_doc['reports']:
#         for c_reports in reports['community_reports']:
#             c_reports['item_image'] = base64.b64encode(c_reports['item_image']).decode('utf-8')
#             report_lists.append(c_reports)
#
#     return render_template('generate_report.html',community_id=community_id,reports=report_lists)
#
#

from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, make_response, Blueprint, Response, flash
from pymongo import MongoClient
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

l_and_f_routes = Blueprint('l_and_f', __name__)

mongo_uri = "mongodb://localhost:27017/mydatabase"
client = MongoClient(mongo_uri)
db = client['NeighbourNet']
l_and_f_collections = db['report_l_and_f']
community_collection = db['Communities']
user_collection = db['User_details']



@l_and_f_routes.route('/generate_report/<community_id>', methods=['POST', 'GET'])
def red_g_report(community_id):
    report = ['a','b']

    print(community_id)
    # print(report)
    # report_lists = []
    # lf_docs = l_and_f_collections.find(
    #     {'community': community_id},
    #     {'reports.community_reports': 1, '_id': 0}
    # )
    # print(report_lists)
    # for doc in lf_docs:
    #     for report in doc['reports']:
    #         for c_report in report['community_reports']:
    #             if c_report.get('item_image'):
    #                 c_report['item_image'] = base64.b64encode(c_report['item_image']).decode('utf-8')
    #             report_lists.append(c_report)
    # print(report_lists)
    return render_template('generate_report.html', community_id=community_id)

@l_and_f_routes.route('/found-button,<reporters_username>,<report_item_name>,<community_id>')
def found_button_by_member(reporters_username,report_item_name,community_id):

    username = session['usermail']

    send_email_to_reporter(username,reporters_username,report_item_name)

    flash(f"Message sent regarding {report_item_name}", "success")

    return redirect(url_for('c_page.render_l_and_f',community_id=community_id))

@l_and_f_routes.route('/close_report,<unique_id_reports>,<community_id>')
def delete_report(unique_id_reports,community_id):

    l_and_f_collections.delete_one({'_id':ObjectId(unique_id_reports)})

    flash(f" Report Deleted", "danger")

    return redirect(url_for('c_page.render_l_and_f', community_id=community_id))

def send_email_to_reporter(my_username,reporters_username,report_item_name):

    from_my = "shaikhshoaib7218@gmail.com"
    password = 'vtvd jglz ppfj asgx'

    user_n = user_collection.find_one({'username': my_username})
    n = user_n.get('first_name')
    l = user_n.get('last_name')

    address = reporters_username

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_my, password)

    msg = MIMEMultipart()
    msg['from'] = from_my
    msg['to'] = address
    msg['subject'] = f"{n} {l} found your Item {report_item_name}"

    msg.attach(MIMEText(f"{n} {l} found your Item {report_item_name} that was lost. You can Contact gim for further enquiries you can use out chatroom."))

    server.send_message(msg)
    server.quit()


