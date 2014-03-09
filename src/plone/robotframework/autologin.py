import os
from plone.robotframework.remotelibrary import RemoteLibrary


class AutoLogin(RemoteLibrary):

    def enable_autologin_as(self, *args):
        if 'robot_login' not in self.acl_users.objectIds():
            self.acl_users._doAddUser('robot_login', 'robot_login', args, '')
        else:
            self.acl_users._doChangeUser('robot_login', 'robot_login', args, '')
        os.environ['HTTP_AUTHORIZATION'] = 'Basic cm9ib3RfbG9naW46cm9ib3RfbG9naW4='

    def disable_autologin(self):
        self.acl_users._doDelUsers('robot_login')
        del os.environ['HTTP_AUTHORIZATION']

from ZServer.HTTPServer import zhttp_handler

get_environment_orig = zhttp_handler.get_environment


def get_environment(self, *args, **kwargs):
    env = self.get_environment_orig(*args, **kwargs)
    if 'HTTP_AUTHORIZATION' in os.environ:
        env['HTTP_AUTHORIZATION'] = os.environ['HTTP_AUTHORIZATION']
    return env

setattr(zhttp_handler, 'get_environment_orig', get_environment_orig)
setattr(zhttp_handler, 'get_environment', get_environment)
