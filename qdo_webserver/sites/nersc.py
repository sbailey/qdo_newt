"""
Site specific backend for NERSC using NEWT
"""
import flask
import requests
import logging
import json

from qdo_webserver.sites.base import BaseSite

#-------------------------------------------------------------------------
class NERSC(BaseSite):
    def __init__(self, hostname='edison'):
        self.hostname = hostname
        self.info = dict(
                sitename = 'NERSC',
                hosts = dict(
                    edison = dict(queues = ['regular', 'debug']),
                    hopper = dict(queues = ['regular', 'debug']),
                    carver = dict(queues = ['regular', 'debug']),
                )
            )
        
    def login(self, username, password):
        """
        See qdo_webserver.sites.base.BaseSite
        """
        data = dict(username=username, password=password)    
        url = "https://newt.nersc.gov/newt/auth/"
        results = requests.post(url, data)
        d = results.json()      #- convert to dictionary
        if results.status_code == 200 and d['auth']:
            d['qdo_authkey'] = d['newt_sessionid']
            del d['newt_sessionid'] 
            d['qdo_username'] = d['username']
            del d['username']
            return d
        else:
            d['status_code'] = results.status_code
            raise RuntimeError(json.dumps(d))
            
    def runcmd(self, cmd, qdo_authkey=None, username=None, hostname=None):
        if hostname is None:
            hostname = self.hostname
            
        if qdo_authkey is None:
            qdo_authkey = flask.request.cookies.get('qdo_authkey')
            
        cmdurl = "https://newt.nersc.gov/newt/command/"+hostname
        data = dict(
            executable=cmd,
            loginenv='true',
        )
        results = requests.post(cmdurl, data, cookies={'newt_sessionid': qdo_authkey})
        return results.json()["output"]
        
        
        
