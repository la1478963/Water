from django.conf.urls import url,include
from rbac import views

urlpatterns = [
    url(r'^$',views.OperationLog.as_view()),
    # url(r'^auth/$',views.Auth.as_view()),

]



