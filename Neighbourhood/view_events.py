from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, make_response, Blueprint, Response
from pymongo import MongoClient

mongo_uri = "mongodb://localhost:27017/"

client = MongoClient(mongo_uri)
db = client['NeighbourNet']
event_collection = db['Events']

view_events_route = Blueprint('ver', '__name__')


@view_events_route.route('/create-event/<community>')
def render_create_event(community):
    print(community)
    return render_template('create_event.html', commo_id=community)

