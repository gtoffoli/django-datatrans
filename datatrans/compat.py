# Django >= 1.4 moves handler404, handler500, include, patterns and url from
# django.conf.urls.defaults to django.conf.urls.
try:
    from django.conf.urls import (handler404, handler500, include, patterns, url)
except ImportError:
    from django.conf.urls.defaults import (handler404, handler500, include, patterns, url)
