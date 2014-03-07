import sys

from robot import run_cli


def pybot():
    # This code hides warnings for known Sphinx-only-directives when
    # executing pybot against Sphinx-documentation:
    from docutils.parsers.rst.directives import register_directive
    from docutils.parsers.rst.roles import register_local_role
    dummy_directive = lambda *args: []
    options = ('maxdepth', 'creates', 'numbered', 'hidden')
    setattr(dummy_directive, 'content', True)
    setattr(dummy_directive, 'options', dict([(opt, str) for opt in options]))
    register_directive('toctree', dummy_directive)
    register_directive('robotframework', dummy_directive)
    register_local_role('ref', dummy_directive)

    # Run pybot
    run_cli(sys.argv[1:])


def robot():
    run_cli(['--listener', 'plone.robotframework.listener.RobotListener']
            + sys.argv[1:])
