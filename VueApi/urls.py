from django.conf.urls import url,include
from VueApi import views

urlpatterns = [
    # url(r'/(?P<service>(\w+))',views.Login.as_view()),
    url(r'',views.VueApi.as_view()),
    # url(r'^release/$',views.Release.as_view()),
    # url(r'^auth/$',views.Auth.as_view()),

]



