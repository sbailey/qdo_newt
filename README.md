qdo webserver
-------------

This package provides a web interface for QDO (kew-doo),
a lightweight toolkit for processing many tasks in a queue.

  * https://bitbucket.org/berkeleylab/qdo
  * https://bitbucket.org/berkeleylab/qdo_webserver
  
Run `bin/qdo_webserver` to start an example session using NERSC as the backend.
  
## Authentication ##

Authentication begins with a POST to {baseurl}/site/login with data
including `username` and `password`.  This returns a response including
the cookies `qdo_authkey` and `qdo_username` that are used for subsequent
authentication.  The response data includes the expiration time of the
authentication key.  For convenience, the data also include `qdo_authkey`
and `qdo_username`; clients may cache these for future use if they aren't
using a session that automatically handles the cookies.

Python example using the requests library:

    #- Basic setup
    import getpass
    import requests

    data = dict()
    data['username'] = 'sjbailey'
    data['password'] = getpass.getpass()

    #- Site login
    baseurl = "http://127.0.0.1:5000"
    r = requests.post(baseurl+'/site/login', data)
    qdo_authkey = r.cookies.get('qdo_authkey')
    qdo_username = r.cookies.get('qdo_username')
    #- or
    qdo_authkey = r.json()['qdo_authkey']
    qdo_username = r.json()['qdo_username']

    #- See queues for this user
    r = requests.get('{}/{}/queues/'.format(baseurl, data['username']), \
        cookies=dict(qdo_authkey=qdo_authkey, qdo_username=qdo_username))

    #- With a session instead
    s = requests.Session()
    r = s.post(baseurl+'/site/login', data)
    r = s.get('{}/{}/queues/'.format(baseurl, data['username']))

## API definition ##

These still need details, but they define the basic set of URLs.

### Get qdo_authkey token
    GET  {baseurl}/site/login
    Returns qdo_authkey authorization token
    
### Get basic site information like name, hosts, and queues
    GET  {baseurl}/site/info
    Returns JSON structure of site information, details TBD
    
### list queues for user
    http:   GET {baseurl}/{user}/queues/
    python: qdo.tojson(qdo.qlist(user=user))

### get queue details
    http:   GET {baseurl}/{user}/queues/{queue}
    python: qdo.tojson(qdo.connect(queue, user=user))
    
### create a new queue
    http:   PUT {baseurl}/{user}/queues/{queue}
    python: qdo.create(queue, user=user)
    
### retry failed tasks in queue
    http:   PUT {baseurl}/{user}/queues/{queue}/retry
    python: qdo.connect(queue, user=user).retry()

### reset running tasks back to pending
    http:   PUT {baseurl}/{user}/queues/{queue}/recover
    python: qdo.connect(queue, user=user).recover()

### pause queue
    http:   PUT {baseurl}/{user}/queues/{queue}/pause
    python: qdo.connect(queue, user=user).pause()

### resume queue
    http:   PUT {baseurl}/{user}/queues/{queue}/resume
    python: qdo.connect(queue, user=user).resume()

### delete the queue
    http: DELETE {baseurl}/{user}/queues/{queue}
    python: qdo.connect(queue, user=user).delete()

### launch jobs to process tasks in queue
    http:   POST {baseurl}/{user}/queues/{queue}/launch
    python: qdo.connect(queue, user=user).launch(...)
    see python qdo docs for many options to launch(...)

### list tasks in queue
    http:   GET {baseurl}/{user}/queues/{queue}/tasks/
    python: qdo.tojson(qdo.connect(queue, user=user).tasks())

### list tasks in queue with filter on state and/or exitcode
    http:   GET {baseurl}/{user}/queues/{queue}/tasks/?state=<state>&exitcode=<exitcode>
    python: qdo.tojson(qdo.connect(queue, user=user).tasks(state=state, exitcode=exitcode))

### add new task(s) to queue
    http:   POST {baseurl}/{user}/queues/{queue}/addtask/
    http:   POST {baseurl}/{user}/queues/{queue}/tasks/
    python:
        qdo.connect(queue, user=user).add(data.command)             #- single task
        qdo.connect(queue, user=user).add_multiple(data.commands)   #- multiple tasks

TODO: document how to distinguish between single task vs. multiple tasks for the REST API

### view a specific task
    http:   GET  {baseurl}/{user}/queues/{queue}/tasks/<taskid>
    python: qdo.tojson(do.connect(queue, user=user).tasks(id=taskid))

### modify a task with state and optionally err and/or message
    http:   PUT  {baseurl}/{user}/queues/{queue}/tasks/<taskid>
    python:
        task = qdo.connect(queue, user=user).tasks(id=taskid)
        task.set_state(state=data.state, err=data.err, message=data.message)
    
### get task and set state=RUNNING as an atomic operation
    http:   POST {baseurl}/{user}/queues/{queue}/poptask
    python: task = qdo.tojson(qdo.connect(queue, user=user).get())

Users calling this function are then expected to run the task and then
use the previous command to update the Task state (e.g. succeeded or failed).


## Developer notes

The URL mapping is defined in qdo_webserver/api.py .  It relies upon a backend
site object for authentication, running qdo commands, and providing information
about the backend site.  The webserver executable sets app.site to that object,
which is available to the URL mapping code as flask.current_app.site .

This package comes with an example implementation for using the
[http://newt.nersc.gov](NEWT) toolkit to authenticate and run commands
at [http://nersc.gov](NERSC).  Additional backend sites could be added by:

  * subclassing qdo_webserver.sites.base.BaseSite and implementing the
    member functions defined there.  These provide
    - a way to authenticate and receive a temporary token
    - a way to run commands on the site using that token
    - an information dictionary about that site
  * updating run.py to use that backend instead of NERSC
  
