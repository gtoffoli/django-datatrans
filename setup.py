#!/usr/bin/env python
from distutils.core import setup

setup(name='django-datatrans',
      version='0.1',
      description='Translate Django models without changing anything to existing applications and their underlying database.',
      author='City Live nv',
      author_email='jef.geskens@citylive.be',
      url='http://github.com/citylive/django-datatrans/',
      packages=['datatrans'],
      license='BSD')
