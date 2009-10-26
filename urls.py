from django.conf.urls.defaults import *
from datatrans import views

urlpatterns = patterns('',
    url(r'^$', views.model_list, name='datatrans_model_list'),
    url(r'^model/(?P<model>.*)/(?P<language>.*)/$', views.model_detail, name='datatrans_model_detail'),
    url(r'^make/messages/$', views.make_messages, name='datatrans_make_messages'),
)
