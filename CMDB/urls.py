"""CMDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from arya.service import v2
from rest_framework.authtoken import views as rest_view
from rbac import views
# from svn import views as svn_views
from app01 import views as app_view
from rbac.views import init
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^arya/', (v2.site.urls, None, 'arya')),
    url(r'^code.html', views.Code),
    url(r'^test', views.Test),
    url(r'^api/',include('release.urls')),
    url(r'^vueapi',include('VueApi.urls')),
    # url(r'^log/',views.OperationLog),
    url(r'^log/',include('rbac.urls')),
    # url('^release/', init.release),
    # url(r'^api-token-auth/', init.obtain_auth_token)
    # url(r'^api-token-auth/', rest_view.obtain_auth_token)
]






