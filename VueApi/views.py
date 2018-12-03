import json
import random
import string
import time
import datetime
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render,HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import get_authorization_header
from django.http import JsonResponse
from rbac import models
from utlis.jiami_class import jiami
from utlis.log_class import Logger
from rbac.service import init_permission
from utlis import serializers_class

request_dic={

}


class VueApi(APIView):
    authentication_classes = []
    def get(self,request,*args,**kwargs):
        self.dispatch()
    def post(self,request,*args,**kwargs):
        pass

    def get_menu(self,request,post_data_dic,ret_dic,token_li):
        #返回的是user_menu
        token=token_li[0]
        user_obj = models.User.objects.filter(token=token)
        ret=init_permission.rest_init_menu(user_obj, request)
        ret_dic['data'] = {'menu_list':ret,'menu_model_list':self.HOME}
        ret_dic['ret'] = 200

    def login(self,request,post_data_dic,ret_dic,token_li):
        '''
        :param post_data_dic:  post请求里面的数据，也是就登录信息
        '''
        username=post_data_dic.get('account').strip('')
        password=post_data_dic.get('password').strip('')
        password=jiami().base_str_encrypt(password).strip()
        remember=post_data_dic.get('remember')
        obj=models.User.objects.filter(username=username,password=password)
        if obj.first():
            ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
            obj.update_or_create(defaults={'token': ran_str})
            # 应该初始化用户登录信息
            ret_dic['ret'] = 200
            ret_dic['data']['token'] = ran_str
            # print('ran_str',ran_str)
            ret_dic['data']['account'] = obj.first().username
            ret_dic['data']['userinfo'] = ''


    def get_title(self,request,post_data_dic,ret_dic,token_li):
        '''
        :param post_data_dic 是 请求体的数据   ret_dic是 返回数据
        '''
        ret_dic['ret'] = 200
        ret_dic['data']['site_name'] = 'scloudpay_CMDB'


