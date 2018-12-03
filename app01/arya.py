import json
import string
from django.core.exceptions import ValidationError
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
from utlis import webssh_class
from utlis.log_class import Logger


#主机
class LableConfig(v2.AryaConfig):
    list_display = ['name']
    # show_add = True
v2.site.register(models.Lable, LableConfig)

class MemoryConfig(v2.AryaConfig):
    list_display = ['size','width','locator','type']
    # show_add = True
v2.site.register(models.Memory, MemoryConfig)


class DiskConfig(v2.AryaConfig):
    list_display = ['path','size',]
v2.site.register(models.Disk, DiskConfig)

class LoginConfig(v2.AryaConfig):
    def login_pwd_base(self,row=None,is_title=None):
        if is_title:
            return '登录密码'
        obj=models.Login.objects.filter(pk=row.id).first()

        ret=jiami_class.jiami().base_str_decrypt(obj.login_pwd)

        return ret

    list_display = ['id','login_name',login_pwd_base]

    def add(self,req):
        '''
        传递self对象
        传递req
        传递 加密解密的 在前段页面中的关键字
        '''
        ret=arya_func.core_add(self,req,'login_pwd')
        self._log_in_db(req, url=self.add_log_url,
                proj=self.mod, action='add', msg='add' + self.mod)
        return ret


    def change(self,req,nid):
        '''
        传递self对象
        传递req
        传递被修改者id
        传递 加密解密的 在前段页面中的关键字
        '''
        ret=arya_func.core_change(self,req,nid,'login_pwd')
        self._log_in_db(req, url=self.update_log_url,
                proj=self.mod, action='update', msg='update' + self.mod)
        return ret

v2.site.register(models.Login, LoginConfig)

class OsConfig(v2.AryaConfig):
    list_display = ['name',]
v2.site.register(models.Os, OsConfig)

class NetworkConfig(v2.AryaConfig):
    list_display = ['ip_address','mac_address']
# v1.site.register(models.Network,NetworkConfig)


class HostConfig(v2.AryaConfig):
    show_ali=True
    _monitor = True
    #网页登录ssh开关
    # _webssh = True

    def detail_view(self,row=None,is_title=None):
        if is_title:
            return '详情'
        app=self.model_class._meta.app_label
        mod=self.model_class._meta.model_name
        _str='arya:%s_%s_detail' %(app,mod)
        url=reverse(viewname=_str,args=(row.id,))
        result='<a href="{0}" class="btn btn-info">查看详情</a>'.format(url)
        return mark_safe(result)

    # def gouzi(self):
        #通过 钩子函数 增加可以解析的URL
        # return [url('^(\d+)/detail.html/', self.detail, name='%s_%s_detail' % (self.app, self.mod)),]

    def detail(self,req,nid):
        if req.method=='GET':
            obj = models.Host.objects.filter(pk=nid).first()
        else:
            hostname=req.POST.get('hostname').strip().lstrip('主机名:')
            from client.bin.run import JG_info
            JG_func = JG_info._begin(no_all_in=hostname)
            # print(JG_func)
            return HttpResponse(JG_func)
        return render(req, 'detail.html', locals())

    def disk(self,row=None,is_title=None):
        if is_title:
            return '磁盘'
        value_list=models.Host.objects.filter(pk=row.id).values('disks__size')
        ret_li=[]
        for value in value_list:
            ret_li.append(value['disks__size'])
        try:
            ret='+'.join(ret_li)
        except TypeError:
            ret = ''
        return ret

    def get_model_form(self):
        if self.model_f:
            return self.model_f
        class Dynamic(ModelForm):
            # def __init__(self, *args, **kwargs):
            #     super(Dynamic, self).__init__(*args, **kwargs)
                # print(self.base_fields.values())
                # print(self.base_fields['hostname'].__dict__)
                # print(self.base_fields['logining'].__dict__)

            loginname=fields.CharField(widget=widgets.Textarea(),label='登录用户')
            # #PasswordInput
            loginpwd=fields.CharField(widget=widgets.Textarea(),label='登录密码')
            # eth0_network=fields.CharField(max_length=32,error_messages=)
            class Meta:
                model=models.Host
                # fields='__all__'
                # exclude=['logining']
                fields=['hostname','ecsname','loginname','loginpwd',
                        'loginname','loginpwd','login_port','logining',
                        'cpu','lab','mem','speed','disks',
                        'eth1_network','eth0_network','sn','os',
                        'kernel','the_upper','source',
                        'state','remarks','state'
                        ]
                error_messages={
                    'eth0_network':{
                        'required': 'ip不能为空'
                    },
                }
                widgets={
                    'hostname': widgets.TextInput(attrs={'class': 'done'}),
                    'ecsname': widgets.TextInput(attrs={'class': 'done'}),
                    'login_port': widgets.TextInput(attrs={'class': 'done'}),
                    'cpu': widgets.TextInput(attrs={'class': 'done'}),
                    'mem': widgets.TextInput(attrs={'class': 'done', }),
                    'eth1_network': widgets.TextInput(attrs={'class': 'done',}),
                    'eth0_network': widgets.TextInput(attrs={'class': 'done', }),
                    'sn': widgets.TextInput(attrs={'class': 'done',}),
                    'speed': widgets.TextInput(attrs={'class': 'done', }),
                    'kernel': widgets.TextInput(attrs={'class': 'done', }),
                    'remarks': widgets.Textarea(attrs={'class': 'done', }),
                    'createtime': widgets.TextInput(attrs={'class': 'done', }),
                    'disks': widgets.SelectMultiple(attrs={'class': 'done', }),
                    'os': widgets.Select(attrs={'class': 'done', }),
                    'state': widgets.Select(attrs={'class': 'done',}),
                    # 'logining':widgets.SelectMultiple(attrs={'class':'displaynone'}) ,
                }
                # def __init__(self,*args,**kwargs):
                #     super(Dynamic, self).__init__(*args,**kwargs)
                #     self.base_fields['logining'].widget.attr.update({'display':'none'})

            def clean(self):
                login_li=[]
                user_li=self.cleaned_data['loginname'].strip().split('\r\n')
                pwd_li=self.cleaned_data['loginpwd'].strip().split('\r\n')
                if len(user_li) != len(pwd_li):
                    self.add_error('loginname',ValidationError('用户名密码数量不一致'))
                    return self.cleaned_data
                for line in range(len(user_li)):
                    jiami_pwd = jiami_class.jiami().base_str_encrypt(pwd_li[line])
                    login_obj=models.Login.objects.filter(login_name=user_li[line],login_pwd=jiami_pwd).first()
                    if not login_obj:
                        login_obj=models.Login.objects.create(login_name=user_li[line], login_pwd=jiami_pwd)
                    login_li.append(login_obj.id)
                self.cleaned_data['logining']=login_li
                return self.cleaned_data


        return Dynamic

    def list(self,request):
        self.request=request
        search_q=request.GET.get('q')
        candition_q=Q()
        search_list=self.aget.get_search_list()
        if search_list and search_q:
            for search_item in search_list:
                temp_q=Q()
                temp_q.children.append((search_item,search_q))
                candition_q.add(temp_q,'OR')

        pteam_obj=request.session.get(settings.PTEAM_OBJ)
        if pteam_obj != 1:
            host_list=request.session.get(settings.PERMISSION_HOST)['host']
            queryset=models.Host.objects.filter(candition_q,pk__in=host_list).order_by('-id')
        else:
            queryset=models.Host.objects.filter(candition_q).order_by('-id')
        data=v2.ChangeList(self, queryset)
        self._log_in_db(request, url=self.list_log_url, proj=self.mod,
                    action='list', msg='list' + self.mod)
        return render(request,'list.html',{'data':data,'req':request})


    def change(self,req,nid):
        log_dic={'user':None,'pwd':None,'hero':None}
        logger=Logger(loglevel=1, logger="fox",num=1).getlog()
        dynamic_form = self.get_model_form()
        obj=self.model_class.objects.filter(id=nid).first()
        if req.method=='GET':
            form = dynamic_form(instance=obj)
            login_name_li=[]
            login_pwd_li=[]
            #剔除loginning中的多对多显示
            form.fields.pop('logining')
            ##拿出loginning中的多对多数据
            logining=form.initial.pop('logining')
            for login_item in logining:
                base_str=jiami_class.jiami().base_str_decrypt(login_item.login_pwd)
                login_name_li.append(login_item.login_name)
                login_pwd_li.append(base_str)
            #通过换行拼接
            _loginname='\r\n'.join(login_name_li)
            _loginpwd='\r\n'.join(login_pwd_li)
            form.initial['loginname']=_loginname
            form.initial['loginpwd']=_loginpwd

            log_dic['user']='\t'.join(login_name_li)
            log_dic['pwd']='\t'.join(login_pwd_li)
            logger.info('%s,%s' %(log_dic['user'],log_dic['pwd']))
            return render(req,'edit.html',{'data':form,'req':req,'tag':True})
        else:
            form = dynamic_form(instance=obj,data=req.POST)
            if form.is_valid():
                form.save()
                log_dic['hero']=req.session.get(settings.USER)
                logger.info('------------The above is %s modification',log_dic['hero'])
                self._log_in_db(req, url=self.update_log_url,
                            proj=self.mod, action='update', msg='update' + self.mod)
                return redirect(self.jump.list_url)
            return render(req, 'edit.html', {'data': form,'req':req})


    #显示月租金
    def cost(self, row=None, is_title=None):
        if is_title:
            return '月租/元'
        obj = models.Host.objects.filter(pk=row.id).first()
        try:
            return obj.remarks
        except:
            return ''


    #监控
    def monitor(self, req, nid):
        if req.method == 'GET':
            start_time,end_time=time_class.Time().ali_def_monitor()
            obj = self.model_class.objects.filter(id=nid)
            monitor_obj=obj.first().hm.filter(
                # timestamp__gte='2018-08-10T06:49:58Z',
                # timestamp__lte='2018-08-10T06:54:58Z')
                timestamp__gte=start_time,
                timestamp__lte=end_time)
            #默认请求
            return render(req, 'monitor.html', locals())
        else:
            get_dic=req.POST
            if get_dic.get('tag'):
                #有条件
                pass
            else:
                #无条件
                obj_li=models.Host.objects.filter(id=nid)
            obj = self.model_class.objects.filter(id=nid).delete()
            self.site._log_in_db(req, url=self.site.delete_log_url,
                            proj=self.site.mod, action='del', msg='del_' + self.site.mod)
            return redirect(self.jump.list_url)

    def add(self,req):
        dynamic_form=self.get_model_form()
        if req.method=='GET':
            form=dynamic_form()
            form.fields.pop('logining')
            # print(form.clean_logining())
            return render(req,'hosts/add.html',{'data':form,'req':req})
        else:
            form=dynamic_form(data=req.POST)
            if form.is_valid():
                form.save()
                self._log_in_db(req, url=self.add_log_url,
                        proj=self.mod, action='add', msg='add' + self.mod)
                return redirect(self.jump.list_url)
            return render(req, 'hosts/add.html', {'data': form,'req':req})

    def app_name(self,row=None,is_title=None):
        if is_title:
            return '应用'
        obj = models.Host.objects.filter(pk=row.id).first()
        str='<a href="/arya/rbac/app/list.html?k={0}">{1}</a>'
        #删除结尾数字
        ret=''
        for item in obj.apphost.all():
            ret+=str.format(item.name.rstrip(string.digits),item.name.rstrip(string.digits))
        return mark_safe(ret)

    list_display = ['hostname',app_name,'cpu','mem',disk,'eth1_network','eth0_network']
    # list_display = ['hostname',app_name,'cpu','mem',disk,'eth1_network','eth0_network']

    search_list = ['eth1_network__contains','eth0_network__contains','hostname__contains']
v2.site.register(models.Host, HostConfig)


class VpcNetConfig(v2.AryaConfig):
    list_display = ['title',]
v2.site.register(models.VpcNet, VpcNetConfig)

class VpcSwitchConfig(v2.AryaConfig):
    list_display = ['title',]
v2.site.register(models.VpcSwitch, VpcSwitchConfig)

class SourceConfig(v2.AryaConfig):
    list_display = ['name']

v2.site.register(models.Source, SourceConfig)


#应用
class AppConfig(v2.AryaConfig):
    def get_model_form(self):
        if self.model_f:
            return self.model_f
        class Dynamic(ModelForm):
            class Meta:
                model=self.model_class
                fields='__all__'
                # widgets={
                #     'hosts':widgets.Select(attrs={'size':10}),
                # }
        return Dynamic

    def ab(self,row=None,is_title=None):
        if is_title:
            return 'AB组'
        ret = models.App.objects.filter(pk=row.id).first().get_ab_display()
        return ret

    def environment(self,row=None,is_title=None):
        if is_title:
            return '主机环境'
        ret = models.App.objects.filter(pk=row.id).first().get_environment_display()
        return ret
    def app_name(self,row=None,is_title=None):
        if is_title:
            return '应用'
        obj = models.App.objects.filter(pk=row.id).first()
        str='<a href="/arya/rbac/app/list.html?k={0}">{1}</a>'
        #删除结尾数字
        q_str=obj.name.rstrip(string.digits)
        ret=str.format(q_str,q_str)
        return mark_safe(ret)

    def hosts(self,row=None,is_title=None):
        if is_title:
            return '主机列表'
        value_list = models.App.objects.filter(pk=row.id).values('hosts__eth0_network')
        str='<a href="/arya/rbac/host/list.html?q={0}">{1}</a>'
        ret=''
        for value in value_list:
            val=value['hosts__eth0_network']
            jg_str=str.format(val,val)
            ret+=jg_str
        return mark_safe(ret)


    def list(self,req):
        self.request=req
        pteam_obj = req.session.get(settings.PTEAM_OBJ)
        if req.GET.get('pteamrole') or req.GET.get('ab') or req.GET.get('environment'):
            get_pteamrole=req.GET.get('pteamrole','')
            get_ab=req.GET.get('ab','')
            get_environment=req.GET.get('environment','')
            search_q = req.GET.get('q','')
            candition_q = Q()
            search_list = self.aget.get_search_list()
            if search_list and search_q:
                for search_item in search_list:
                    temp_q = Q()
                    temp_q.children.append((search_item, search_q))
                    candition_q.add(temp_q, 'OR')
            get_ab_tag=''
            get_environment_tag=''
            filter_q={}
            if get_pteamrole:
                filter_q['pteamrole__groupname']=get_pteamrole
            if get_ab:
                for i in models.App.ab_choices:
                    if get_ab in i :
                        filter_q['ab']=i[0]
                        continue
            if get_environment:
                for i in models.App.environment_choices:
                    if get_environment in i :
                        filter_q['environment']=i[0]
                        continue
            if pteam_obj != 1:
                app_list = req.session.get(settings.PERMISSION_HOST)['app']
                queryset = models.App.objects.filter(candition_q,**filter_q,pk__in=app_list).order_by('-id')
            else:
                queryset=models.App.objects.filter(candition_q,**filter_q).order_by('-id')

        #通过点击A标签的跳转
        elif req.GET.get('k'):
            self.request = req
            search_q = req.GET.get('k')
            candition_q = Q()
            #拿到需要匹配的列表
            accurate_list = self.aget.get_accurate_list()
            if accurate_list and search_q:
                for accurate_item in accurate_list:
                    #由于测试、灰度环境的应用名不带数字，生产环境的带数字，所以要匹配到xxx1,xxx,xxx2等
                    ser_li=['','temp_a', 'temp_b', 'temp_c', 'temp_d', 'temp_e']
                    for i in ser_li:
                        #列表第一个值为了匹配 没有数字的(灰度，测试等环境)
                        JG=str(ser_li.index(i)) if ser_li.index(i) !=0 else ''
                        # JG=str(ser_li.index(i) + 1)
                        i = Q()
                        #拼接生产环境的字符串偶偶额怒
                        i.children.append((accurate_item, search_q+JG))
                        candition_q.add(i, 'OR')
            if pteam_obj != 1:
                #获取 权限所能看见的主机列表
                app_list = req.session.get(settings.PERMISSION_HOST)['app']
                queryset = models.App.objects.filter(candition_q, pk__in=app_list).order_by('-id')
            else:
                queryset = models.App.objects.filter(candition_q).order_by('-id')

        else:
            self.request = req
            search_q = req.GET.get('q')
            candition_q = Q()
            search_list = self.aget.get_search_list()
            if search_list and search_q:
                for search_item in search_list:
                    temp_q = Q()
                    temp_q.children.append((search_item, search_q))
                    candition_q.add(temp_q, 'OR')
            if pteam_obj != 1:
                app_list = req.session.get(settings.PERMISSION_HOST)['app']
                queryset = models.App.objects.filter(candition_q,pk__in=app_list).order_by('-id')
            else:
                queryset = models.App.objects.filter(candition_q).order_by('-id')

        data = v2.ChangeList(self, queryset)
        return render(req, 'list.html', {'data': data, 'req': req})


    list_display = [app_name, 'pteamrole',ab,environment,hosts]

    search_list = ['name__contains',
                    'hosts__eth0_network__contains',
                    # 'name'
                    ]
    accurate_list=['name',]


    def search_button_list(self):
        button_list = [
            ['项目组', [], 'pteamrole'],
            ['组', ['A', 'B', 'VPC'], 'ab'],
            ['环境', ['开发环境', '测试环境', '灰度环境', '压测环境', '生产环境'], 'environment']
        ]
        obj_l=models.Pteam.objects.all()
        for obj in obj_l:
            button_list[0][1].append(obj.groupname)
        return button_list

v2.site.register(models.App, AppConfig)





