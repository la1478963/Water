from __future__ import absolute_import, unicode_literals
import time
import requests
from celery import shared_task
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.shortcuts import render,HttpResponse,redirect


from rbac import models

@shared_task
def add(x,y):
    return x+y


@shared_task
def log_indb(user_id,url,proj=None,action=None,explain=None,msg=None):
    '''
    OperationLog 都是数据库的字段
    :param msg:  标识，登录(login) 增删改查,  发布 等
    :return:
    '''
    in_dic={'user_id':user_id,'url':url}
    if proj:
        in_dic['proj']=proj
    if action:
        in_dic['action']=action
    if explain:
        in_dic['explain']=explain
    models.OperationLog.objects.create(**in_dic)
    if not msg:
        ret_str=''
        return ret_str
    ret_str=msg+'  be put in storage'
    return ret_str



@shared_task
def mul(x, y):
    print(x*y)
    return x * y


@shared_task
def xsum(numbers):
    print(sum(numbers))
    return sum(numbers)