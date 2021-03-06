# -*- coding: utf-8 -*-
import argparse
import logging
import sys
import time
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

from plone.robotframework.remotelibrary import RemoteLibrary
from plone.robotframework.listener import LISTENER_PORT
from plone.robotframework.listener import LISTENER_HOST

HAS_VERBOSE_CONSOLE = False

TIME = lambda: time.strftime('%H:%M:%S')
START = lambda msg:  '%s [\033[35m start \033[0m] %s' % (TIME(), msg)
END = lambda msg:  '%s [\033[35m end \033[0m] %s' % (TIME(), msg)
WAIT = lambda msg:  '%s [\033[33m wait \033[0m] %s' % (TIME(), msg)
ERROR = lambda msg: '%s [\033[31m ERROR \033[0m] %s' % (TIME(), msg)
READY = lambda msg: '%s [\033[32m ready \033[0m] %s' % (TIME(), msg)


def start(zope_layer_dotted_name):

    print WAIT("Starting Zope 2 server")

    zsl = Zope2Server()
    zsl.start_zope_server(zope_layer_dotted_name)

    print READY("Started Zope 2 server")

    listener = SimpleXMLRPCServer((LISTENER_HOST, LISTENER_PORT),
                                  logRequests=False)
    listener.register_function(zsl.zodb_setup_and_log, 'zodb_setup')
    listener.register_function(zsl.zodb_teardown_and_log, 'zodb_teardown')

    try:
        listener.serve_forever()
    finally:
        print
        print WAIT("Stopping Zope 2 server")

        zsl.stop_zope_server()

        print READY("Zope 2 server stopped")


def zope_server():
    parser = argparse.ArgumentParser()
    parser.add_argument('layer')
    VERBOSE_HELP = (
        '-v information about test layers setup and tear down, '
        '-vv add logging.WARNING messages, '
        '-vvv add INFO messages, -vvvv add DEBUG messages.')
    parser.add_argument('--verbose', '-v', action='count', help=VERBOSE_HELP)
    args = parser.parse_args()
    if args.verbose:
        global HAS_VERBOSE_CONSOLE
        HAS_VERBOSE_CONSOLE = True
        loglevel = logging.ERROR - (args.verbose - 1) * 10
    else:
        loglevel = logging.ERROR
    logging.basicConfig(level=loglevel)
    try:
        start(args.layer)
    except KeyboardInterrupt:
        pass


class RobotListener:

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        server_listener_address = 'http://%s:%s' % (
            LISTENER_HOST, LISTENER_PORT)
        self.server = xmlrpclib.ServerProxy(server_listener_address)

    def start_test(self, name, attrs):
        self.server.zodb_setup()

    def end_test(self, name, attrs):
        self.server.zodb_teardown()

ZODB = RobotListener  # BBB


class Zope2Server:

    def __init__(self):
        self.zope_layer = None
        self.extra_layers = {}

    def _import_layer(self, layer_dotted_name):
        parts = layer_dotted_name.split('.')
        if len(parts) < 2:
            raise ValueError('no dot in layer dotted name')
        module_name = '.'.join(parts[:-1])
        layer_name = parts[-1]
        __import__(module_name)
        module = sys.modules[module_name]
        layer = getattr(module, layer_name)
        return layer

    def start_zope_server(self, layer_dotted_name):
        new_layer = self._import_layer(layer_dotted_name)
        if self.zope_layer and self.zope_layer is not new_layer:
            self.stop_zope_server()
        setup_layer(new_layer)
        self.zope_layer = new_layer

    def set_zope_layer(self, layer_dotted_name):
        """Explicitly set the current Zope layer, when you know what you are
        doing
        """
        new_layer = self._import_layer(layer_dotted_name)
        self.zope_layer = new_layer

    def amend_zope_server(self, layer_dotted_name):
        """Set up extra layers up to given layer_dotted_name"""
        old_layers = setup_layers.copy()
        new_layer = self._import_layer(layer_dotted_name)
        setup_layer(new_layer)
        for key in setup_layers.keys():
            if key not in old_layers:
                self.extra_layers[key] = 1
        self.zope_layer = new_layer

    def prune_zope_server(self):
        """Tear down the last set of layers set up with amend_zope_server"""
        tear_down(self.extra_layers)
        self.extra_layers = {}
        self.zope_layer = None

    def stop_zope_server(self):
        tear_down()
        self.zope_layer = None

    def zodb_setup_and_log(self, name):
        if HAS_VERBOSE_CONSOLE:
            print
            print START(name)
        self.zodb_setup()
        return True

    def zodb_teardown_and_log(self, name):
        self.zodb_teardown()
        if HAS_VERBOSE_CONSOLE:
            print END(name)
        return True

    def zodb_setup(self, layer_dotted_name=None):
        if layer_dotted_name:
            self.set_zope_layer(layer_dotted_name)

        from zope.testing.testrunner.runner import order_by_bases
        layers = order_by_bases([self.zope_layer])
        for layer in layers:
            if hasattr(layer, 'testSetUp'):
                if HAS_VERBOSE_CONSOLE:
                    print WAIT("Test set up %s.%s" % (
                        layer.__module__, layer.__name__))
                layer.testSetUp()
        if HAS_VERBOSE_CONSOLE:
            print READY("Test set up")

    def zodb_teardown(self, layer_dotted_name=None):
        if layer_dotted_name:
            self.set_zope_layer(layer_dotted_name)

        from zope.testing.testrunner.runner import order_by_bases
        layers = order_by_bases([self.zope_layer])
        layers.reverse()
        for layer in layers:
            if hasattr(layer, 'testTearDown'):
                if HAS_VERBOSE_CONSOLE:
                    print WAIT("Test tear down %s.%s" % (
                        layer.__module__, layer.__name__))
                layer.testTearDown()
        if HAS_VERBOSE_CONSOLE:
            print READY("Test torn down")


setup_layers = {}


def setup_layer(layer, setup_layers=setup_layers):
    assert layer is not object
    if layer not in setup_layers:
        for base in layer.__bases__:
            if base is not object:
                setup_layer(base, setup_layers)
        if hasattr(layer, 'setUp'):
            if HAS_VERBOSE_CONSOLE:
                print WAIT("Set up %s.%s" % (
                    layer.__module__,
                    layer.__name__
                ))
            layer.setUp()
        setup_layers[layer] = 1


def tear_down(setup_layers=setup_layers):
    from zope.testing.testrunner.runner import order_by_bases
    # Tear down any layers not needed for these tests. The unneeded layers
    # might interfere.
    unneeded = [l for l in setup_layers]
    unneeded = order_by_bases(unneeded)
    unneeded.reverse()
    for l in unneeded:
        try:
            try:
                if hasattr(l, 'tearDown'):
                    if HAS_VERBOSE_CONSOLE:
                        print WAIT("Tear down %s.%s" % (
                            l.__module__,
                            l.__name__
                        ))
                    l.tearDown()
            except NotImplementedError:
                pass
        finally:
            del setup_layers[l]


class Zope2ServerRemote(RemoteLibrary):
    """Provides ``remote_zodb_setup`` and ``remote_zodb_teardown`` -keywords to
    allow explicit test isolation via remote library calls when server is set
    up with robot-server and tests are run by a separate pybot process.

    *WARNING* These keywords does not with zope.testrunner (yet).
    """
    def remote_zodb_setup(self, layer_dotted_name):
        Zope2Server().zodb_setup(layer_dotted_name)

    def remote_zodb_teardown(self, layer_dotted_name):
        Zope2Server().zodb_teardown(layer_dotted_name)
