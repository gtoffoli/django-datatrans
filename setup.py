#!/usr/bin/env python
from setuptools import (setup, find_packages)
import datatrans

LONG_DESCRIPTION = """

"""

setup(name='django-datatrans',
      version=datatrans.__version__,
      description='Translate Django models without changing anything to existing applications and their '
                  'underlying database.',
      long_description=LONG_DESCRIPTION,
      author='Jef Geskens, VikingCo nv',
      author_email='jef.geskens@mobilevikings.com',
      url='http://github.com/citylive/django-datatrans/',
      license='LICENSE',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      classifiers=[
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

