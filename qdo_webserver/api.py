#!/usr/bin/env python

"""
A test of a simple qdo server

Stephen, Shreyas, and Gonzalo
Spring 2015
"""

import json
import requests

from flask import Flask, url_for, make_response
import flask
app = Flask(__name__)

__version__ = "0.1"

#-------------------------------------------------------------------------
#- Login / authentication / site info

@app.route('/site/login', methods=['POST', 'GET'])
def login():
    """
    Returns results with qdo_authkey cookie and data including keys
    """
    if flask.request.method=='POST':
        username = flask.request.form.get('username')
        password = flask.request.form.get('password')
        try:
            results = flask.current_app.site.login(username, password)
        except RuntimeError:
            #- TODO: what should this be?
            return "error", 404
            
        results['links'] = dict(queues = flask.request.url_root+url_for('queues', username=username))
        response = make_response(json.dumps(results))
        response.set_cookie('qdo_authkey', results['qdo_authkey'])
        response.set_cookie('qdo_username', results['qdo_username'])
        return response
    else:
        return '''
        <form action="/site/login" method="post">
            <p>Enter your NERSC username and password</p>
            <p>username<input type=text name=username>
            <p>password<input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        '''

@app.route('/site/info/', methods=['GET'])
def siteinfo():
    return flask.jsonify(flask.current_app.site.info)

#-------------------------------------------------------------------------
#- Hello World

@app.route('/')
def start():
    """
    Returns hello world introdution message
    """
    response = dict()
    response['version'] = __version__
    response['info'] = "This is the REST API for QDO (kew-doo), a lightweight toolkit for processing many tasks in a queue."
    response['links'] = dict(
        login = flask.request.url_root+'site/login',
        qdo = 'https://bitbucket.org/berkeleylab/qdo',
        qdo_webserver = 'https://bitbucket.org/berkeleylab/qdo_webserver',
        )
    return flask.jsonify(response)

#-------------------------------------------------------------------------
#- qdo REST API
#- Examples, far from complete

@app.route('/<username>/')
@app.route('/<username>/queues/')
def queues(username):
    cmd = "python -c 'import qdo; print qdo.tojson(qdo.queues())' "
    return flask.current_app.site.runcmd(cmd)
    
@app.route('/<username>/queues/<queuename>/')
def queue(username, queuename):
    cmd = """python -c 'import qdo; print qdo.tojson(qdo.connect("{}"))' """.format(queuename)
    return flask.current_app.site.runcmd(cmd)
    
@app.route('/<username>/queues/<queuename>/tasks/')
def tasks(username, queuename):
    cmd = """python -c 'import qdo; print qdo.tojson(qdo.connect("{}").tasks())' """.format(queuename)
    return flask.current_app.site.runcmd(cmd)

@app.route('/<username>/queues/<queuename>/tasks/<taskid>', methods=['POST', 'GET'])
def task(username, queuename, taskid):
    #- POST: add a new task to the queue
    if flask.request.method=='POST':
        return "Not implemented", 501
    elif flask.request.method == 'GET':
        #- GET: take a look at an existing Task
        cmd = """python -c 'import qdo; print qdo.tojson(qdo.connect("{}").tasks("{}") )' """.format(queuename, taskid)
        return flask.current_app.site.runcmd(cmd)
        
@app.route('/<username>/queues/<queuename>/poptask/')
def get(username, queuename):
    cmd = """python -c 'import qdo; print qdo.tojson(qdo.connect("{}").get()') """.format(queuename)
    return flask.current_app.site.runcmd(cmd)
    
#- ...

