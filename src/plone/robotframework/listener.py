# -*- coding: utf-8 -*-
import xmlrpclib
import os

ZSERVER_HOST = os.getenv("ZSERVER_HOST", "localhost")
LISTENER_HOST = os.getenv("LISTENER_HOST", ZSERVER_HOST)
LISTENER_PORT = int(os.getenv("LISTENER_PORT", 10001))


class RobotListener:

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        server_listener_address = 'http://%s:%s' % (
            LISTENER_HOST, LISTENER_PORT
        )
        self.server = xmlrpclib.ServerProxy(server_listener_address)

    def start_test(self, name, attrs):
        self.server.zodb_setup(name)

    def end_test(self, name, attrs):
        self.server.zodb_teardown(name)
