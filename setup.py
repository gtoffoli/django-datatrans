#!/usr/bin/env python
from distutils.core import setup

setup(name='django-datatrans',
      version='0.6',
      description='Translate Django models without changing anything to existing applications and their underlying database.',
      author='City Live nv',
      author_email='jef.geskens@citylive.be',
      url='http://github.com/citylive/django-datatrans/',
      packages=['datatrans'],
      license='BSD',
      include_package_data = True,
      package_data = {'datatrans': ['templates/datatrans/*'],},
      zip_safe = False,
      classifiers = [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Topic :: Software Development :: Internationalization',
      ],
)
