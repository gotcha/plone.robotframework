# -*- coding: utf-8 -*-
from OFS.SimpleItem import SimpleItem


class RemoteLibrary(SimpleItem):
    """Robot Framework remote library base for Plone

    http://robotframework.googlecode.com/hg/doc/userguide/RobotFrameworkUserGuide.html?r=2.7.7#remote-library-interface
    http://robotframework.googlecode.com/hg/tools/remoteserver/robotremoteserver.py

    """
    def get_keyword_names(self):
        """Return names of the implemented keywords
        """
        blacklist = dir(SimpleItem)
        blacklist.extend([
            'get_keyword_names',
            'get_keyword_arguments',
            'get_keyword_documentation',
            'run_keyword'
        ])
        names = filter(lambda x: x[0] != '_' and x not in blacklist, dir(self))
        return names

    def get_keyword_arguments(self, name):
        """Return keyword arguments
        """
        return None

    def get_keyword_documentation(self, name):
        """Return keyword documentation
        """
        func = getattr(self, name, None)
        if func:
            return func.__doc__
        else:
            return u''

    def run_keyword(self, name, args, kwargs={}):
        """Execute the specified keyword with given arguments.
        """
        func = getattr(self, name, None)
        result = {'error': '', 'return': ''}
        try:
            retval = func(*args, **kwargs)
        except Exception, e:
            result['status'] = 'FAIL'
            result['error'] = str(e)
        else:
            result['status'] = 'PASS'
            result['return'] = retval
            result['output'] = retval
        return result
