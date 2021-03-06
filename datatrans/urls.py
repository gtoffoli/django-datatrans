from django.conf.urls import url
from datatrans import views

urlpatterns = [
    url(r'^$', views.model_list, name='datatrans_model_list'),
    url(r'^model/(?P<slug>.*)/(?P<language>.*)/(?P<object_id>.*)/$', views.object_detail, name='datatrans_object_detail'),
    url(r'^model/(?P<slug>.*)/(?P<language>.*)/$', views.model_detail, name='datatrans_model_detail'),
    url(r'^make/messages/$', views.make_messages, name='datatrans_make_messages'),
    url(r'^obsoletes/$', views.obsolete_list, name='datatrans_obsolete_list'),
    url(r'^translate/(?P<model>.*)/(?P<pk>.*)/$', views.translate)
]
