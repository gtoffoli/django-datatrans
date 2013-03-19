#!/usr/bin/env python
from distutils.core import setup
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
      license='LICENSE.txt',
      packages=['datatrans'],
      include_package_data=True,
      package_data={'datatrans': ['templates/datatrans/*'], },
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

