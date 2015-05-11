class BaseSite(object):
    """
    Defines the base class interface for site-specific functionality
    
    Each site should subclass this and replace login() and runcmd()
    """
    def __init__(self):
        pass
        
    def login(self, username, password):
        """
        Given a valid username and password, return a qdo_authkey token via
        a dictionary with keys:
            - qdo_authkey
            - username
            - duration      (key validity in seconds)
            - expiration    (TODO: explain...)
            - other site-specific keys may be present
        """
        raise NotImplementedError
        
    def runcmd(self, cmd, username, qdo_authkey):
        """
        Run cmd on the site using username/qdo_authkey for authentication
        """
        raise NotImplementedError
        
    def info(self):
        """
        Return dictionary of information about this site
        """
        raise NotImplementedError
