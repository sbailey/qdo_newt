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
    results = requests.post(url, data)
    if results.status_code == 200:
        res_obj = results.json()
        newt_sessionid = res_obj['newt_sessionid']
        res_obj['qdo_authkey'] = res_obj['newt_sessionid']
        del res_obj['newt_sessionid'] 

        response = make_response(json.dumps(res_obj))
        response.set_cookie('qdo_authkey', newt_sessionid)
        return response
    else:
        return "error", 404    
        
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

def runcmd(cmd, hostname='hopper'):
    """
    Uses NEWT to run a command on the requested NERSC host
    """
    cmdurl = "https://newt.nersc.gov/newt/command/"+hostname
    qdo_authkey = flask.request.cookies.get('qdo_authkey')
    data = dict(
        executable=cmd,
        loginenv='true',
    )
    results = requests.post(cmdurl, data, cookies={'newt_sessionid': qdo_authkey})
    return results.json()["output"]

@app.route('/<username>/')
@app.route('/<username>/queues/')
def qlist(username):
    ### cmd = "python -c 'import qdo; print [q.summary() for q in qdo.qlist()]' "
    cmd = "python -c 'import qdo; print qdo.qlist()' "
    return runcmd(cmd)
    
@app.route('/<username>/queues/<queuename>/')
def queue(username, queuename):
    cmd = """python -c 'import qdo; print repr(qdo.connect("{}"))' """.format(queuename)
    return runcmd(cmd)
    
@app.route('/<username>/queues/<queuename>/tasks/')
def tasks(username, queuename):
    cmd = """python -c 'import qdo; print qdo.connect("{}").tasks()' """.format(queuename)
    return runcmd(cmd)

@app.route('/<username>/queues/<queuename>/tasks/<taskid>', methods=['POST', 'GET'])
def task(username, queuename, taskid):
    #- POST: add a new task to the queue
    if flask.request.method=='POST':
        return "Not implemented", 501
    elif flask.request.method == 'GET':
        #- GET: take a look at an existing Task
        cmd = """python -c 'import qdo; print qdo.connect("{}").tasks("{}")' """.format(queuename, taskid)
        return runcmd(cmd)
        
#- Should we rename this?
@app.route('/<username>/queues/<queuename>/get/')
def get(username, queuename):
    cmd = """python -c 'import qdo; print qdo.connect("{}").get()' """.format(queuename)
    return runcmd(cmd)
    
#-----
#- Super basic HTML login example
#- Your browser will then cache the authentication cookie and use it for
#- other calls to this API.
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

            res_obj = results.json()
            newt_sessionid = res_obj['newt_sessionid']
            res_obj['qdo_authkey'] = res_obj['newt_sessionid']
            del res_obj['newt_sessionid'] 

            response = make_response(json.dumps(res_obj))
            response.set_cookie('qdo_authkey', newt_sessionid)
            return response
        else:
            return "error", 404

    else:
        return '''
        <form action="/login/" method="post">
            <p>Enter your NERSC username and password</p>
            <p>username<input type=text name=username>
            <p>password<input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        '''

if __name__ == "__main__":
    app.run(debug=True)