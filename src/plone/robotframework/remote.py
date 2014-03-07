# -*- coding: utf-8 -*-
from plone.testing import Layer
from plone.testing.z2 import zopeApp

from plone.robotframework.remotelibrary import RemoteLibrary


class RemoteLibraryLayer(Layer):

    libraryBases = ()

    def __init__(self, *args, **kwargs):
        kwargs['name'] = kwargs.get('name', 'RobotRemote')
        self.libraryBases = (RemoteLibrary,) + kwargs.pop('libraries', ())
        super(RemoteLibraryLayer, self).__init__(*args, **kwargs)

    def setUp(self):
        id_ = self.__name__.split(':')[-1]
        assert id_ not in globals(), "Conflicting remote library id: %s" % id_
        globals()[id_] = type(id_, self.libraryBases, {})
        for app in zopeApp():
            app._setObject(id_, globals()[id_]())

    def tearDown(self):
        id_ = self.__name__.split(':')[-1]
        for app in zopeApp():
            if id_ in app.objectIds():
                app._delObject(id_)
        del globals()[id_]
