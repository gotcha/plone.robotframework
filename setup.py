from setuptools import setup, find_packages
import os

version = '1.0'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')
console_scripts = [
    "robot-server = plone.robotframework.zopeserver:zope_server",
    "robot = plone.robotframework.robotentrypoints:robot",
    "pybot = plone.robotframework.robotentrypoints:robot",
]

entry_points = dict(console_scripts=console_scripts)

debug_requires = [
    'robotframework-debuglibrary',
]

setup(name='plone.robotframework',
      version=version,
      description="Robot framework Zope2 integration",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Godefroid Chapelle',
      author_email='gotcha@bubblenet.be',
      url='https://github.com/plone/plone.robotframework',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'argparse',
          'plone.testing',
      ],
      extras_require={'debug': debug_requires},
      entry_points=entry_points,
      )
