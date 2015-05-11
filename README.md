qdo webserver
=============

This package provides a web interface for QDO (kew-doo),
a lightweight toolkit for processing many tasks in a queue.

  * https://bitbucket.org/berkeleylab/qdo
  * https://bitbucket.org/berkeleylab/qdo_webserver
  
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

### Get qdo_authkey token
    GET  {baseurl}/site/login
    Returns qdo_authkey authorization token
    
### Get basic site information like name, hosts, and queues
    GET  {baseurl}/site/info
    Returns JSON structure of site information, details TBD
    
### list queues for user
    http:   GET {baseurl}/users/{user}/queues/
    python: qdo.qlist(user=user)

GET  {baseurl}/<user>/queues/<queue>
    - get queue details
    - python: repr(qdo.connect(queue, user=user))
    
PUT  {baseurl}/<user>/queues/<queue>
    - create a new queue
    - python: qdo.create(queue, user=user)
    
PUT  {baseurl}/<user>/queues/<queue>/retry
    - retry failed tasks in queue
    - python: qdo.connect(queue, user=user).retry()

PUT  {baseurl}/<user>/queues/<queue>/recover
    - reset running tasks back to pending
    - python: qdo.connect(queue, user=user).recover()

PUT  {baseurl}/<user>/queues/<queue>/pause
    - pause queue
    - python: qdo.connect(queue, user=user).pause()

PUT  {baseurl}/<user>/queues/<queue>/resume
    - resume queue
    - python: qdo.connect(queue, user=user).resume()

DELETE {baseurl}/<user>/queues/<queue>
    - delete the queue
    - python: qdo.connect(queue, user=user).delete()

POST {baseurl}/<user>/queues/<queue>/launch
    - launch jobs to process tasks in queue
    - qdo.connect(queue, user=user).launch(...)
    - see python qdo docs for many options to launch
    
GET  {baseurl}/<user>/queues/<queue>/tasks/
    - list tasks in queue
    - python: qdo.connect(queue, user=user).tasks()

GET  {baseurl}/<user>/queues/<queue>/tasks/?state=<state>&exitcode=<exitcode>
    - list tasks in queue with filter on state and/or exitcode
    - python: qdo.connect(queue, user=user).tasks(state=state, exitcode=exitcode)
    
POST {baseurl}/<user>/queues/<queue>/addtask/
POST {baseurl}/<user>/queues/<queue>/tasks/
    - add new task to queue
    - qdo.connect(queue, user=user).add(data.command)

POST {baseurl}/<user>/queues/<queue>/addtasks/
POST {baseurl}/<user>/queues/<queue>/batchtasks/
    - add multiple new tasks to queue
    - qdo.connect(queue, user=user).add_multiple(data.commands)
    - better name?  add_multiple?  batch_add?
    - combine with addtask using introspection for single vs. multiple?
    
GET  {baseurl}/<user>/queues/<queue>/tasks/<taskid>
    - view a specific task
    - qdo.connect(queue, user=user).tasks(id=taskid)
    
PUT  {baseurl}/<user>/queues/<queue>/tasks/<taskid>
    - modify a task with state and optionally err and/or message
    - task = qdo.connect(queue, user=user).tasks(id=taskid)
    - task.set_state(state=data.state, err=data.err, message=data.message)
    
POST {baseurl}/<user>/queues/<queue>/get
POST {baseurl}/<user>/queues/<queue>/poptask
    - get task and set state=RUNNING as an atomic operation
    - python: task = qdo.connect(queue, user=user).get()
    --> better name?  poptask?  get?  run?

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
  
