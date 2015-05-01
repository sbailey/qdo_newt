#!/usr/bin/env python

"""
A test of a simple qdo server

Stephen, Shreyas, and Gonzalo
Spring 2015
"""

import json


import requests

from flask import Flask, escape, url_for, make_response
import flask
app = Flask(__name__)

@app.route('/')
def start():
    r = dict()
    r['version'] = qdo.__version__
    r['info'] = """\
QDO (kew-doo) is a lightweight toolkit for processing many tasks in a queue.
This is the web api for that toolkit.  Start at {baseurl}/{username} for
a list of queues for that user."""
    return flask.jsonify(r)

@app.route('/<username>/')
@app.route('/<username>/queues/')
def qlist(username):
    newt_session_id = flask.request.cookies.get('qdo_auth_key')
    data = dict(
        ### executable="bash -lc 'qdo list'",
        executable="python -c 'import qdo; print [q.summary() for q in qdo.qlist()]' ",
        loginenv='true',
    )
    url = "https://newt.nersc.gov/newt/command/hopper/"
    results = requests.post(url, data, cookies={'newt_sessionid': newt_session_id})

    return results.text
    ### return flask.jsonify(results.contents)
    
#-------------------------------------------------------------------------
    
@app.route('/<username>/queues/<queuename>/')
def queue(username, queuename):
    r = dict(command="qdo status "+queuename)
    return flask.jsonify(r)

@app.route('/<username>/queues/<queuename>/tasks/')
def tasks(username, queuename):
    r = dict(command='qdo tasks '+queuename)
    return flask.jsonify(r)

@app.route('/<username>/queues/<queuename>/tasks/<taskid>', methods=['POST', 'GET'])
def task(username, queuename, taskid):
    try:
        q = qdo.connect(queuename, user=username)
    except ValueError:
        flask.abort(404)
        
    if flask.request.method == 'GET':
        r = dict(command='no direct qdo command line equivalent to get details for a single task')
    elif flask.request.method == 'POST':
        r = dict(command="qdo add {} 'command to run...'".format(queuename))
    
    return flask.jsonify(r)

@app.route('/<username>/queues/<queuename>/get/')
def get(username, queuename):
    r = dict(command="no direct qdo CL equivalent to get a single task and change its state to running")
    return flask.jsonify(r)
    
@app.route('/login/', methods=['GET', 'POST'])
def login():

    if flask.request.method=='POST':
        data = dict(
            username = flask.request.form['username'],
            password = flask.request.form['password']
        )

        url = "https://newt.nersc.gov/newt/auth/"
        results = requests.post(url, data)
        if results.status_code == 200:
            newt_sessionid = results.json()['newt_sessionid']
            response = make_response(results.text)
            response.set_cookie('qdo_auth_key', newt_sessionid)
            return response
        else:
            return "error", 404

    else:
        return '''
        <form action="/login/" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        '''


if __name__ == "__main__":
    app.run(debug=True)