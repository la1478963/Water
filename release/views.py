import json
import random
import string
import time
import datetime
import traceback
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render,HttpResponse
from rest_framework.views import APIView
from django.http import JsonResponse
from rbac import models
from utlis.jiami_class import jiami
from utlis.log_class import Logger


class Release(APIView):
    logger = Logger(loglevel=1, logger="fox",num=2).getlog()
    main_ret_dic = {'status': False, 'tag': 'send', 'error': None, 'state': ''}
    environment_list = (
        (1, 'develop'),
        (2, 'test'),
        (3, 'gray'),
        (4, 'pressure'),
        (5, 'production'),
    )
    def get(self,req,*args,**kwargs):
        #脚本向 CMDB获取数据
        state=req.data.get('state')
        tag=req.data.get('tag')
        self.logger.info(tag)
        self.logger.info(state)
        data_dic = req.data.get('data')

        ret_dic = self.main_ret_dic
        ret_dic['state'] = 'build'
        ret_dic['tag'] = 'get'

        # if state!='pack' and tag!='get':
        if state!='build' and tag!='get':
            self.logger.error('tag is ERROR:'+tag)
            ret_dic['error']='state,tag is error'
            return JsonResponse(ret_dic)

        timestamp, app, environment, package_dic, conf_dic,build_status=\
            self.get_data(data_dic)

        if not environment:
            self.logger.error('environment is ERROR:' + environment)
            ret_dic['error'] = 'environment is non'
            ret_dic['status'] = False
            return JsonResponse(ret_dic)


        pack_obj=models.Package.objects.filter(disname=package_dic.get('name'))
        if not pack_obj.first():
            self.logger.info('request error,pack_name is ERROR:' + package_dic.get('name'))
            ret_dic['error'] = 'pack  is error'
            ret_dic['status'] = False
            return JsonResponse(ret_dic)

        # app_obj=models.Package.objects.filter(disname=package_dic.get('name'),proj__name=app)
        # app_obj=pack_obj.first().proj.filter(name=app)

        # app_obj=models.Project.objects.filter(name=app,tag=2)
        if not models.Package.objects.filter(disname=package_dic.get('name'),proj__name=app,proj__tag=2).first():
            self.logger.info('request error,app or app tag is ERROR  :' + app)
            ret_dic['error'] = 'app is non or app tag is error'
            ret_dic['status'] = False
            return JsonResponse(ret_dic)

        # print('package_dic-----',package_dic.get('name'))
        # pack_obj=app_obj.first().pj.filter(disname=package_dic.get('name'))
        # # pack_obj=app_obj.first().pj.filter(disname=package_dic.get('name'),md5=package_dic.get('md5'))
        # if not pack_obj.first():
        #     self.logger.error('pack_name is ERROR:' + package_dic.get('name'))
        #     ret_dic['error'] = 'pack  is error'
        #     ret_dic['status'] = False
        #     return JsonResponse(ret_dic)

        pack_obj_md5=pack_obj.filter(md5=package_dic.get('md5'))
        if not pack_obj_md5.first():
            self.logger.info('request error,pack_md5 is ERROR:' + str(package_dic.get('md5')))
            ret_dic['error'] = 'md5  is error'
            return JsonResponse(ret_dic)

        #获取返回数据
        pack_source_path=pack_obj_md5.first().osspath
        num = [list[0] for list in self.environment_list if environment in list ]
        if not num:
            self.logger.info('request error,environment tag is ERROR  :' + num)
            ret_dic['error'] = 'environment  is error'
            return JsonResponse(ret_dic)
        # get获取app名，和环境    向数据库获取 对应的ip 和部署路径
        app_obj=models.App.objects.filter(name=app,environment=num[0]).first()
        try:
            server_path = app_obj.path
            #in_ip 实际是 字符串，因为测试环境和灰度环境 只有一台，所以不会出现列表的状态
            #部署的脚本修改起来比较麻烦，所以尽量不改
            JG_dic = {'in_ip': '', 'server_path': server_path, 'pack_source_path': pack_source_path}
            JG_dic['app'] = app
            JG_dic['package'] = package_dic.get('name')
            for i in app_obj.hosts.all():
                JG_dic['in_ip']+=i.eth0_network+' '
                # JG_dic['in_ip'].append(i.eth0_network)
            ret_dic['status'] = True
            ret_dic['data'] = JG_dic
            return JsonResponse(ret_dic)
        # except KeyError:
        except AttributeError:
            self.logger.info('request error,app and environment  is non ')
            ret_dic['error'] = 'app and environment  is non'
            return JsonResponse(ret_dic)


    def get_data(self,get_data_dic,):
        packagetype_choices = models.Package.packagetype_choices
        timestamp = get_data_dic.get('timestamp', '')
        self.logger.info('timestamp:' + str(timestamp) + '; timestamp_type:' + str(type(timestamp)))
        #支持传递俩种时间格式，时间戳，和str的时间格式
        if not isinstance(timestamp,int):
            #如果不是int类型
            try:
                timestamp=int(timestamp)
            except ValueError as e:
                timestamp_dt=time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                timestamp = int(time.mktime(timestamp_dt))
        app = get_data_dic.get('app', '')
        if app:
            app=app.strip('')
        environment = get_data_dic.get('environment', '')
        package = get_data_dic.get('package')
        build_status = get_data_dic.get('build_status')
        package_dic={}
        conf_dic={}
        for key,val in package.items():
            if not val:
                continue
            if key =='jar' or key =='war':
                package_dic['name']=val[0]
                package_dic['osspath']=val[1]
                package_dic['md5']=val[2]
                if key =='jar':
                    package_dic['tag']=2
                else:
                    package_dic['tag'] = 1
            else:
                for item in packagetype_choices:
                    if item[1]==key:
                        conf_dic[item[0]]=val
                        break
        #记录日志，发送的具体数据: app 环境  包名  路径  md5
        self.logger.info(
            'app:'+str(app)+
            'environment:'+str(environment)+' '+
            'package_name'+str(package_dic['name'])+' '+
            'package_source_path'+str(package_dic['osspath'])+' '+
            'package_md5'+str(package_dic['md5'])+' '+
            'build_status'+str(build_status)
        )
        return (timestamp,app,environment,package_dic,conf_dic,build_status)


    def post(self,req,*args,**kwargs):
        get_state = req.data.get('state')
        get_data_dic = req.data.get('data')
        #首次脚本向CMDB发送数据
        if get_state == 'pack':
            ret_dic=self.pack(get_state,get_data_dic)


        elif get_state == 'build':
            ret_dic = self.main_ret_dic
            ret_dic['state'] = 'build'
            # 处理脚本发送来的数据
            timestamp, app, environment, package_dic, conf_dic ,build_status = \
                self.get_data(get_data_dic)
            if build_status:
                # 获取部署后的状态
                env_num = [list[0] for list in self.environment_list if environment in list]
                #如果是jar包 那么可能有多个包,那么就创建多个部署记录
                for item in package_dic['name']:
                    package_obj=models.Package.objects.filter(disname=item,proj__name=app)
                    ######这是一个新表，部署记录表
                    if package_obj:
                        models.Record.objects.create(
                            timestamp=int(time.time()),
                            status=build_status,
                            project=package_obj.proj,
                            package=package_obj,
                            env=env_num,
                        )
            else:
                    # 处理部署灰度后的 将war包改名的 操作
                pack_li = []
                try:
                    with transaction.atomic():
                        pro_obj = models.Project.objects.filter(name=app, tag=2)
                        if not pro_obj.first():
                            ret_dic['error'] = str(app) + ' is not packed'
                            return JsonResponse(ret_dic)
                        env_obj = models.RecordEnv.objects.filter(name=environment).first()
                        # 更新 包名
                        pro_obj.first().pj.filter(Q(disname__endswith='war') | Q(disname__endswith='jar'), bool=True). \
                            update(
                            disname=package_dic.get('name'), osspath=package_dic.get('osspath')
                        )
                        pack_obj = models.Package.objects.filter(
                            disname=package_dic.get('name'), bool=True).first()
                        pack_li.append(pack_obj)

                        # 操作配置文件
                        for tag, val in conf_dic.items():
                            for i in val:
                                conf_obj = models.Package.objects.filter(disname=i).first()
                                pack_li.append(conf_obj)

                        if environment == 'gray':
                            # 修改项目标识，以免重复
                            pro_obj.update(tag=3)
                            # print(pro_obj.first().tag)
                    ret_dic['status'] = True
                except ValueError as e:
                    self.logger.error(traceback.format_exc())
                    ret_dic['error'] = str(e)

        elif get_state == 'prod':
            # 接受正式环境部署信息
            pass
        else:
            pass

        return JsonResponse(ret_dic)


    #用于收包入库方法
    def pack(self,get_state,get_data_dic):
        ret_dic = self.main_ret_dic
        ret_dic['state'] = 'pack'
        # 记录日志，请求类型，请求方式
        self.logger.info(ret_dic.get('tag') + ' SUCCESS')
        self.logger.info(get_state)

        # 第一次接受包信息
        timestamp, app, environment, package_dic, conf_dic,build_status = \
            self.get_data(get_data_dic)

        if not package_dic.get('name'):
            ret_dic['error'] = 'package_name is not null'
            return JsonResponse(ret_dic)
        try:
            pro_obj,true_false = models.Project.objects.get_or_create(name=app,tag=1)
            # 获取结果(obj,bool)
            models.Package.objects.create(
                disname=package_dic.get('name'),
                osspath=package_dic.get('osspath'),
                md5=package_dic.get('md5'),
                ctime=timestamp,
                proj=pro_obj,
                type=package_dic.get('tag')
            )
            ret_dic['status'] = True
        except ValueError as e:
            ret_dic['error'] = str(e)
        return ret_dic



class Auth(APIView):
    authentication_classes = []
    def get(self,request,*args,**kwargs):
        self.dispatch()

    def post(self,request,*args,**kwargs):

        tok_dic = {'token': 'username,password is ERROR', 'status': False}
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        pwd = jiami().base_str_encrypt(password).strip()
        obj = models.User.objects.filter(username=username, password=pwd)
        if obj.first():
            ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
            tok_dic['status'] = True
            tok_dic['token'] = ran_str
            obj.update_or_create(defaults={'token':ran_str})
        return JsonResponse(tok_dic)






