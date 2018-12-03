from django.conf.urls import url,include
from release import views

urlpatterns = [
    url(r'^release/$',views.Release.as_view()),
    url(r'^auth/$',views.Auth.as_view()),

]



