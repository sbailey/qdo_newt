#!/usr/bin/env python

"""
A test of a simple qdo server

Stephen, Shreyas, and Gonzalo
Spring 2015
"""

import json
import requests

from flask import Flask, escape, url_for
import flask
app = Flask(__name__)

@app.route('/')
def start():
    r = dict()
    r['version'] = "0.1"
    r['info'] = """\
QDO (kew-doo) is a lightweight toolkit for processing many tasks in a queue.
This is the web api for that toolkit.  Start at {baseurl}/{username} for
a list of queues for that user."""
    return flask.jsonify(r)

@app.route('/auth', methods=['POST'])
def auth():
    data = dict(
        username = flask.request.form.get('username'),
        password = flask.request.form.get('password'),
        )
    
    url = "https://newt.nersc.gov/newt/auth/"
    r = requests.post(url, data)
    
    #- rename newt_sessionid -> qdo_authkey
    results = r.json()
    results['qdo_authkey'] = results['newt_sessionid']
    del results['newt_sessionid']
    
    return json.dumps(results)
    
"""
import getpass
import requests

#- Get newt_sessionid from NEWT authorization; cache that somehow
url = "https://newt.nersc.gov/newt/auth/"
data = dict()
data['username'] = 'sjbailey'
data['password'] = getpass.getpass()
results = requests.post(url, data)
newt_sessionid = results.json()['newt_sessionid']

#- then use that newt_sessionid, passing in as a cookie that flask will pick
#- up and use with its call to NEWT
r = requests.get("http://127.0.0.1:5000/sjbailey/queues/", cookies={'newt_sessionid': newt_sessionid})
"""

def runcmd(cmd):
    hostname = 'hopper'
    cmdurl = "https://newt.nersc.gov/newt/command/"+hostname
    qdo_authkey = flask.request.cookies.get('qdo_authkey')
    data = dict(
        executable=cmd,
        loginenv='true',
    )
    results = requests.post(cmdurl, data, cookies={'newt_sessionid': qdo_authkey})
    return results.text

@app.route('/<username>/')
@app.route('/<username>/queues/')
def qlist(username):
    cmd = "python -c 'import qdo; print [q.summary() for q in qdo.qlist()]' "
    return runcmd(cmd)
    
@app.route('/<username>/queues/<queuename>/')
def queue(username, queuename):
    cmd = "python -c 'import qdo; print qdo.connect({})".format(queuename)
    return runcmd(cmd)
    
#----
@app.route('/<username>/queues/<queuename>/tasks/')
def tasks(username, queuename):
    r = dict(command='qdo tasks '+queuename)
    return flask.jsonify(r)

@app.route('/<username>/queues/<queuename>/tasks/<taskid>', methods=['POST', 'GET'])
def task(username, queuename, taskid):
    return "not implemented"

@app.route('/<username>/queues/<queuename>/get/')
def get(username, queuename):
    r = dict(command="no direct qdo CL equivalent to get a single task and change its state to running")
    return flask.jsonify(r)
    
if __name__ == "__main__":
    app.run(debug=True)