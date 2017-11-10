New project
===========

This repository has just been born by importing from https://github.com/vikingco/django-datatrans (Latest commit e60cbf4 on Apr 27, 2016).
I plan to port datatrans to Python 3 and to include some important extensions that already in use inside a large multi-language platform: see http://www.commonspaces.eu/it/info/i18n/ .
For now I left unchanged the remaining part of this README.

Deprecated
==========

Important note: this package is not maintained anymore. We recommend looking at django-parler: https://pypi.python.org/pypi/django-parler


django-datatrans
================

Authors:

* Jef Geskens <jef.geskens@mobilevikings.com>
* Koen Vossen <koen.vossen@mobilevikings.com>
* Gert Van Gool <gert.vangool@citylive.be>
* Béres Botond <botondus@gmail.com>
* Robin Allen

Important note when upgrading to version 0.1.2
----------------------------------------------
The migration script adds a new unique index, like it was before. But this can fail because duplicates might exist
in the database. The new unique index on the model KeyValue consists out of the
following fields: ('language', 'content_type', 'field', 'object_id', 'digest')

You can make sure manually that you don't have duplicate entries in your database or you can use the following command
to delete duplicates:

    python manage.py deleteduplicates

It retains the oldest record and deletes the newest duplicates.  It only works for mysql since it executes raw queries,
this is way more faster that using the south api (it lasts for hours).

Features
--------
* Translate Django models without changing anything to existing applications and their underlying database.
* Uses a registration approach.
* All translations are stored in one extra lookup table. Existing database tables remain untouched.
* Recovery and cleanup of obsolete translations.
* Translation admin interface included (uses CSS from django admin).
* Transparent model API (in 99% of all cases, nothing has to be changed to original code).
* Infinite caching for all strings (based on id and hash)

How to use
----------
1. Add it to INSTALLED_APPS
2. Syncdb
3. Register models (example for FlatPage model):

    from datatrans.utils import register

    class FlatPageTranslation(object):
        fields = ('title', 'content')

    register(FlatPage, FlatPageTranslation)

4. Include the datatrans.urls in your urlconf somewhere, and point your browser to it!
5. Translate away!

Note: you can also search through your objects using translated query strings with the
`datatrans_filter` on your manager. For example:

    FlatPageTranslation.objects.datatrans_filter(title__icontains='zoek dit', language='nl')

will return a QuerySet containing those objects whose dutch title contains the
string 'zoek dit'. Note that this filter API is not identical to Django's, read the docstring
for more info.
