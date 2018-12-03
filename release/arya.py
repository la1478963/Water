import json
import string
import time
from django.core import serializers
from django.db import transaction
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.forms import ModelForm
from django.forms import Form
from django.forms import fields
from django.forms import widgets
from django.db.models import Q
from django.conf import settings
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.conf.urls import url,include
from django.shortcuts import HttpResponse,render,redirect
from arya.service import v2
from rbac import models
from utlis import jiami_class
from utlis import time_class
from utlis import arya_func
from utlis.log_class import Logger
from .utlis import project_file_func
from app01.task import add,mul,log_indb
from clientapi.task import ali_func,alirds_func



class JiraVersionConfig(v2.AryaConfig):
    def jira_name(self, row=None, is_title=None):
        if is_title:
            return 'jira'
        value_list = models.JiraVersion.objects.filter(pk=row.id).values('jira__name')
        ret_li = []
        str = '<a href="/arya/rbac/jiraversion/list.html?q={0}">{1}</a>'
        ret = ''
        for value in value_list:
            val = value['jira__name']
            jg_str = str.format(val, val)
            ret += jg_str
        return mark_safe(ret)

    @csrf_exempt
    def add(self,req):
        ret_dic={'data':None,'msg':True,'status':True,'error':None}
        if req.method=='GET':
            log_indb.delay(req.session.get(settings.USERID),
                           '/arya/rbac/jiraversion/add.html', proj='jiraversion',action='add', msg='add_jiraversion')
            get_name=req.GET.get('name','')
            get_tag=req.GET.get('tag','')  #(1,0)  1代表刚入库  0 代表 入库后，操作过(配置发布完:2 , 部署灰度完:3)
            get_pronum=req.GET.get('pro_num','')
            print('get_pronum---',get_pronum)
            if get_name:
                ret=[]
                if get_tag:
                    get_tag=int(get_tag)
                if get_tag==1:
                    #刚入库
                    package_obj=models.Project.objects.filter(name=get_name,tag=1)
                else:
                        #入库后 编辑 get_tag==0
                    package_obj = models.Project.objects.filter(
                        name=get_name, tag__in=[2,3],
                        jira__jiraver__time=get_pronum
                    )
                if package_obj.first():
                    # package_li=models.Project.objects.filter(name=get_name,tag=1).order_by('pj__packenv')\
                    package_li=package_obj.order_by('pj__packenv')\
                        .values('pj__id','pj__disname','pj__ctime','pj__type',
                                'pj__bool','pj__packenv','name','pj__serverpath',
                                'pj__pack__env__name',
                                )
                    for package in package_li:
                        # print(package['pj__pack__env__name'])
                        ret.append(dict(package))
                    ret_dic['data']=ret
                    log_indb.delay(req.session.get(settings.USERID),
                       '/arya/rbac/jiraversion/add.html', explain='add_app',
                       msg='add_app')
                else:
                    ret_dic['msg']=False
                    ret_dic['error']='无此项目'
                return HttpResponse(json.dumps(ret_dic))

            #通过按钮渲染增加包
            get_id = req.GET.get('id')
            if get_id:
                models.Package.objects.filter(pk=get_id).update(bool=1)
                package=models.Package.objects.filter(pk=get_id).values(
                    'id', 'disname', 'ctime', 'bool','type', 'packenv',
                    'proj__name','serverpath'
                )
                ret_dic['msg']=True
                ret_dic['data']=dict(package[0])
                log_indb.delay(req.session.get(settings.USERID),
                           '/arya/rbac/jiraversion/add.html', explain='add_package',
                               msg='add_package')
                return HttpResponse(json.dumps(ret_dic))

            get_did=req.GET.get('did')
            if get_did:
                models.Package.objects.filter(pk=get_did).update(bool=0)
                package=models.Package.objects.filter(pk=get_did).values(
                    'id', 'disname', 'ctime', 'bool','type', 'packenv',
                    'proj__name','serverpath'
                )
                ret_dic['msg']=True
                ret_dic['data'] = dict(package[0])
                log_indb.delay(req.session.get(settings.USERID),
                               '/arya/rbac/jiraversion/add.html', explain='del_app',
                               msg='del_app')
                return HttpResponse(json.dumps(ret_dic))

            get_oid=req.GET.get('oid','')
            if get_oid :
                models.Package.objects.filter(pk=get_oid).update(proj='')
                ret_dic['msg'] = True
                log_indb.delay(req.session.get(settings.USERID),
                               '/arya/rbac/jiraversion/add.html', explain='del_other',
                               msg='del_other')
                return HttpResponse(json.dumps(ret_dic))
            jira_version = models.JiraVersion.objects.create(time=int(time.time()))
            obj_li = models.Project.objects.filter(jira__isnull=True)

        elif req.method=='DELETE':
            #页面取消操作
            try:
                key,val=req.body.decode().split('=')
                models.JiraVersion.objects.filter(time=val).delete()
            except Exception as e:
                ret_dic['error']=str(e)
                ret_dic['msg']=False
            log_indb.delay(req.session.get(settings.USERID),
                           '/arya/rbac/jiraversion/add.html',
                           explain='cancel', msg='cancel')
            return HttpResponse(json.dumps(ret_dic))

        else:
            #获取页面 唯一值
            json_data=req.POST.get('data')
            get_data=json.loads(json_data)
            jira=get_data.get('jira','')
            version=get_data.get('version','')
            timestamp=get_data.get('timestamp','')
            with transaction.atomic():
                #通过jira name 和  jira version 判断是不是 存在
                jira_obj,created = models.Jira.objects.get_or_create(name=jira)
                if not created and  version in list(i.version for i in jira_obj.jiraver.all()):
                    ret_dic['msg']=False
                    ret_dic['error']='The jiraversion has already existed '
                    return HttpResponse(json.dumps(ret_dic))
                #如果 正常，则 继续向下创建，  先创建 jira name  version    timestamp
                models.JiraVersion.objects.filter(time=timestamp).update(version=version, jira=jira_obj)
                project_dic=get_data.get('project','')
                for project_name,value in project_dic.items():
                    #将 项目与jira关联
                    pro_obj=models.Project.objects.filter(name=project_name,tag=1)
                    pro_obj.update(jira=jira_obj)
                    files=value.get('files','')
                    for k,v in files.items():
                        if v:
                            for item in v:
                                pack_type=item.get('type')
                                pack_osspath=item.get('osspath')
                                pack_name=item.get('name')
                                pack_serverpath=item.get('path','')
                                pack_env=item.get('env','')
                                tag=7
                                for t in models.Package.packagetype_choices:
                                    if pack_type ==t[1]:
                                        tag = t[0]
                                        break

                                models.Package.objects.create(
                                    osspath=pack_osspath,
                                    disname=pack_name,
                                    proj=pro_obj.first(),
                                    ctime=int(time.time()),
                                    type=tag,
                                    serverpath=pack_serverpath,
                                    packenv=pack_env,
                                )
                    # 修改项目标识状态，以免重复
                    pro_obj.update(tag=2)
            log_indb.delay(req.session.get(settings.USERID),
                           '/arya/rbac/jiraversion/add.html', explain='post_data',
                           msg='post_data')
            return HttpResponse(json.dumps(ret_dic))

        return render(req, 'version/addversion.html', locals())



    @csrf_exempt
    def change(self,req,nid):
        obj=models.JiraVersion.objects.filter(id=nid).first()
        ret = {'data': obj, 'msg': True, 'status': True, 'error': None}
        if req.method=='GET':
            try:
                proj_li = models.Jira.objects.filter(pk=obj.jira.id).first().jr.all()
                ret['proj']=proj_li
            except AttributeError:
                pass
            log_indb.delay(req.session.get(settings.USERID),
                           '/arya/rbac/jiraversion/update.html', proj='jiraversion',
                           action='update', msg='update_jiraversion')
            return render(req,'version/editversion.html',{'ret':ret,'req':req})

        else:
            # 获取页面 唯一值
            json_data = req.POST.get('data')
            get_data = json.loads(json_data)
            jira = get_data.get('jira', '')
            timestamp = get_data.get('timestamp', '')
            project_dic = get_data.get('project', '')
            with transaction.atomic():
                #修改 流程号等主内容，无视版本号
                jira_obj,bol=models.Jira.objects.get_or_create(name=jira)
                JiraVer_obj=models.JiraVersion.objects.filter(id=nid)
                JiraVer_obj.update(time=timestamp,jira=jira_obj)



                #下面好像没什么用... , 渲染关联包的时候 ajax 走的add函数
                for project_name, value in project_dic.items():
                    # 将 项目与jira关联
                    pro_obj = models.Project.objects.filter(name=project_name)
                    files = value.get('files', '')
                    for k, v in files.items():
                        if v:
                            for item in v:
                                pack_type = item.get('type')
                                pack_osspath = item.get('osspath')
                                pack_name = item.get('name')
                                pack_serverpath = item.get('path', '')
                                pack_env = item.get('env', '')
                                tag = 7
                                for t in models.Package.packagetype_choices:
                                    if pack_type == t[1]:
                                        tag = t[0]
                                        break
                                models.Package.objects.create(
                                    osspath=pack_osspath,
                                    disname=pack_name,
                                    proj=pro_obj.first(),
                                    ctime=time.time(),
                                    type=tag,
                                    serverpath=pack_serverpath,
                                    packenv=pack_env,
                                )

            ret['data']='success'
            log_indb.delay(req.session.get(settings.USERID),
                           '/arya/rbac/jiraversion/update.html',
                           explain='post_data', msg='post_data')
            return HttpResponse(json.dumps(ret))



    list_display = ['time',jira_name]
v2.site.register(models.JiraVersion, JiraVersionConfig)

class JiraConfig(v2.AryaConfig):

    def version(self, row=None, is_title=None):
        if is_title:
            return '版本号'
        value_list = models.Jira.objects.filter(pk=row.id).values('jiraver__version')
        ret_li = []
        str = '<a href="/arya/rbac/jira/list.html?q={0}">{1}</a>'
        ret = ''
        for value in value_list:
            val = value['jiraver__version']
            jg_str = str.format(val, val)
            ret += jg_str
        return mark_safe(ret)


    list_display = ['name',version]
    # show_add = True
v2.site.register(models.Jira, JiraConfig)


class ProjectConfig(v2.AryaConfig):

    def gouzi(self):
        return []
        # return [url('^(\d+)/configproj.html', self.configproj, name='%s_%s_configproj' % (self.app, self.mod)), ]

    def configproj(self,req,nid):
        if req.method=='GET':
            obj = models.Project.objects.filter(pk=nid).first()
            package_li=models.Package.objects.filter(proj_id=nid).order_by('-id')
        else:

            jira=req.POST.get('jira','')
            proj_name=req.POST.get('name','')
            ji_obj,true_fals=models.Jira.objects.get_or_create(name=jira)
            models.Project.objects.filter(pk=nid).update(jira=ji_obj)
            package_li = req.FILES.getlist('package','')
            sql_li = req.FILES.getlist('sql','')
            conf_li = req.FILES.getlist('conf','')

            data_obj=project_file_func.Data_Processing(nid)
            if package_li:
                data_obj.func_file_li(package_li)
            if sql_li:
                data_obj.func_file_li(sql_li)
            if conf_li:
                data_obj.func_file_li(conf_li)

            return redirect('/arya/rbac/project/list.html')
        return render(req, 'configproj.html', locals())


    #开关在核心代码静态配置
    def configproj_view(self,row=None,is_title=None):
        if is_title:
            return '开发、测试入口'
        app=self.model_class._meta.app_label
        mod=self.model_class._meta.model_name
        _str='arya:%s_%s_configproj' %(app,mod)
        url=reverse(viewname=_str,args=(row.id,))
        result='<a href="{0}" class="btn btn-info">配置项目</a>'.format(url)
        return mark_safe(result)


    def tag_chioces(self,row=None,is_title=None):
        if is_title:
            return '进度'
        ret = models.Project.objects.filter(pk=row.id).first().get_tag_display()
        return ret


    def jira(self,row=None,is_title=None):
        if is_title:
            return 'jira_id'
        ret = models.Project.objects.filter(pk=row.id).first()
        try:
            return ret.jira.name
        except AttributeError:
            return ''

    list_display = ['name',jira,tag_chioces]
    # show_add = True
v2.site.register(models.Project, ProjectConfig)


class PackageConfig(v2.AryaConfig):
    def ctime(self,row=None,is_title=None):
        if is_title:
            return '创建时间'
        ret = models.Package.objects.filter(pk=row.id).first()
        t = time_class.Time.stamp_to_t(ret.ctime)
        return t


    def proj(self,row=None,is_title=None):
        if is_title:
            return 'jira_id'
        ret = models.Package.objects.filter(pk=row.id).first()
        try:
            return ret.proj.name
        except AttributeError:
            return ''

    list_display = ['disname','osspath',ctime,'packenv',proj]
    # show_add = True
v2.site.register(models.Package, PackageConfig)



class RecordConfig(v2.AryaConfig):
    def time(self,row=None,is_title=None):
        if is_title:
            return '时间'
        ret = models.Record.objects.filter(pk=row.id).first()
        t=time_class.Time.stamp_to_t(ret.timestamp)
        return t


    def project(self,row=None,is_title=None):
        if is_title:
            return '包'
        value_list = models.Record.objects.filter(pk=row.id).values('package__disname')
        ret_li = []
        for value in value_list:
            ret_li.append(value['package__disname'])
        try:
            ret = '+'.join(ret_li)
        except TypeError:
            ret = ''
        return ret
    list_display = [time,'project',project,'env','status']
    # show_add = True
v2.site.register(models.Record, RecordConfig)


class RecordEnvConfig(v2.AryaConfig):
    list_display = ['name']
    # show_add = True
v2.site.register(models.RecordEnv, RecordEnvConfig)







