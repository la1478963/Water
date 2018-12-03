import json
import os
import time
import datetime
import importlib
import re
import requests
from datetime import timedelta
from io import BytesIO

from django.db import transaction
from django.db.models import Q
from rest_framework.views import APIView
from django.http import JsonResponse
from django.shortcuts import render,HttpResponse,redirect
from rbac import models
from django.conf import settings
from rbac.service.init_permission import init_permission
from rbac.service.init_permission import rest_init_menu
from django.views.decorators.csrf import csrf_exempt,csrf_protect

from utlis import check_code
from utlis.mail_class import SendMail
from utlis.form_class import LoginForm
from utlis.jiami_class import jiami
from utlis.form_class import RegisterForm
# from utlis.salt_api import SaltApi
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from app01.task import log_indb

class Init(object):
    def __init__(self):
        self.token=''
        self.key='0SM35tyB%'
        self.name=['jenkins','ansible']
    def home(self,request):
        if request.method=='GET':
            return render(request,'home.html',{'req':request})
        else:
            time_li = []
            ms_li = []
            ret_dic={'status':True,'time':time_li,'ms':ms_li}
            path = '/mnt/www/pinglog/'
            D = datetime.datetime.now().strftime('%Y%m%d')
            path = path + D
            with open('1', 'r') as r:
            # with open(path, 'r') as r:
                JG_li = r.read().split('\n')
                for item in JG_li:
                    try:
                        t, ms = item.split(' ')
                        # print(t,ms)
                        time_li.append(t)
                        ms_li.append(ms)
                    except ValueError:
                        pass
            if len(time_li)>60:
                ret_dic['time']=time_li[-60:]
                ret_dic['ms']=ms_li[-60:]
            return HttpResponse(json.dumps(ret_dic))


    def login(self,request):
        if request.method=='GET':
            form=LoginForm()
            return render(request,'login.html',locals())
        else:
            tag = {'msg': True, 'data': None, 'status': True}
            form = LoginForm(data=request.POST)
            if form.is_valid():
                code = request.POST.get('code').upper()
                if request.session[settings.CODEIMG].upper() != code:
                    tag['status'] = False
                    tag['data'] = '验证码错误'
                else:
                    form.cleaned_data['password']=jiami().base_str_encrypt(form.cleaned_data['password']).strip()
                    obj = models.User.objects.filter(**form.cleaned_data)
                    if not obj:
                        tag['status'] = False
                        tag['data'] = '用户名密码错误'
                    else:
                        #初始化 用户数据
                        init_permission(obj, request)

                        #打入日志，登录成功
                        log_indb.delay(request.session.get(settings.USERID),
                                       '/arya/login/',explain='login',msg='login')
            else:
                tag['msg']=False
                tag['data']=form.errors
            return HttpResponse(json.dumps(tag))


    def logout(self,request):
        log_indb.delay(request.session.get(settings.USERID),
                       '/arya/logout/', explain='logout', msg='logout')
        request.session.clear()
        return redirect('/arya/login/')

    def register(self,request):
        if request.method == 'GET':
            form = RegisterForm()
            return render(request, 'register.html', locals())
        if request.method == 'POST':
            tag = {'status': True, 'data': None, 'msg': True}
            form = RegisterForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                obj = models.User.objects.filter(username=username)
                if obj:
                    tag['status'] = False
                    tag['data'] = '用户名已存在'
                else:
                    password = form.cleaned_data['password']
                    password = jiami().base_str_encrypt(password)
                    models.User.objects.create(username=username, password=password)
            else:
                tag['msg'] = False
                tag['data'] = form.errors

            return HttpResponse(json.dumps(tag))
        return render(request,'register.html',locals())

    def sendmail(self,req):
        mailto_list = ['liang@scloudpay.com']
        # mailto_list = ['liang@scloudpay.com','quhebin@scloudpay.com']
        today = str(datetime.date.today() + timedelta(days=15))
        host=''
        val=models.Host.objects.filter(expirytime__lt=today).values('eth1_network')
        for item in val:
            if item.get('eth1_network'):
                host+=item.get('eth1_network')+'\r\n'
        if not host:
            return HttpResponse("failed!")
        sm_obj = SendMail(mailto_list)
        for i in range(len(mailto_list)):  # 发送1封，上面的列表是几个人，这个就填几
            if sm_obj.send_mail(mailto_list, "服务器到期预警",
                                '还有15天到期的服务器ip'+host):  # 邮件主题和邮件内容
                # 这是最好写点中文，如果随便写，可能会被网易当做垃圾邮件退信
                return HttpResponse('done!')
            else:
                return HttpResponse("failed!")


def Code(request):
    img_obj, code = check_code.create_validate_code()
    stream = BytesIO()
    img_obj.save(stream, 'png')
    request.session[settings.CODEIMG] = code
    return HttpResponse(stream.getvalue())


@csrf_exempt
def Test(request):
    from rbac.models import User

    obj = User.objects.filter(username='liang')
    ret = rest_init_menu(obj, request)

    # dic={'name':None,'osspath':None,'type':None}
    # get_sql=request.FILES.get('sql','')
    # get_conf =  request.FILES.get('conf','')
    # get_package =  request.FILES.get('package','')
    # if get_sql:
    #     dic['name']=get_sql.name
    #     dic['osspath']='/1/2/x.sql'
    #     dic['type']=get_sql.name.rsplit('.')[-1]
    # if get_conf:
    #     dic['name'] = get_conf.name
    #     dic['osspath'] = '/1/2/x.sql'
    #     dic['type'] = get_conf.name.rsplit('.')[-1]
    # if get_package:
    #     dic['name'] = get_package.name
    #     dic['osspath'] = '/1/2/x.sql'
    #     dic['type'] = get_package.name.rsplit('.')[-1]
    return HttpResponse(json.dumps(ret))







#系统日志 ajax 请求  暂时没用
class OperationLog(APIView):
    authentication_classes = []
    def get(self,request,*args,**kwargs):
        get_num = request.query_params.get('num')
        ret_dic={'data':None,'status':True}
        ret_li = []
        if get_num:
            obj_li = models.OperationLog.objects.all().order_by('-id')[int(get_num):]
            for obj in obj_li:
                ret_str = '<div class="log_remark">'
                ret_str += '<span style="color: red">{0}  </span>'.format(obj.user.name)
                ret_str += '操作时间:'
                ret_str += '<span style="color: red">{0}  </span> '.format(obj.ctime)
                ret_str += 'url:'
                ret_str += '<span style="color: red">{0}  </span>'.format(obj.url)
                ret_str += 'proj:'
                ret_str += '<span style="color: red">{0}  </span>'.format(obj.proj)
                ret_str += '动作:'
                ret_str += '<span style="color: red">{0}  </span>'.format(obj.action)
                ret_str += '说明:'
                ret_str += '<span style="color: red">{0}  </span>'.format(obj.explain)
                ret_str += '</div>'
                ret_li.append(ret_str)
        ret_dic['data']=ret_li
        return JsonResponse(ret_dic)

    def post(self,request,*args,**kwargs):
        self.dispatch()



init=Init()