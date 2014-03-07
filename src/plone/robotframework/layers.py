from plone.testing import z2

from plone.robotframework.remote import RemoteLibraryLayer
from plone.robotframework.zopeserver import Zope2ServerRemote


REMOTE_LIBRARY_FIXTURE = RemoteLibraryLayer(
    bases=(z2.STARTUP,),
    libraries=(Zope2ServerRemote,),
    name="REMOTE_LIBRARY_FIXTURE"
)
