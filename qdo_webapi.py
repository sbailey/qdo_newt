#!/usr/bin/env python

"""
A test of a simple qdo server

Stephen, Shreyas, and Gonzalo
Spring 2015
"""

import json
import qdo
from qdo import Task

import requests

from flask import Flask, escape, url_for
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
    data = dict(
        ### executable="bash -lc 'qdo list'",
        executable="python -c 'import qdo; print [q.summary() for q in qdo.qlist()]' ",
        loginenv='true',
    )
    url = "https://newt.nersc.gov/newt/command/hopper/"
    results = requests.post(url, data, cookies={'newt_sessionid': "xxx"})

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
    
if __name__ == "__main__":
    app.run(debug=True)