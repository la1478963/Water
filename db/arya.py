import json
from django.utils.safestring import mark_safe

from django.conf import settings
from django.core.urlresolvers import reverse
from django.conf.urls import url,include
from django.shortcuts import HttpResponse,render,redirect
from rbac import models
from django.forms import ModelForm
from django.forms import Form
from django.forms import fields
from django.forms import widgets

from utlis import jiami_class
from utlis import arya_func
from arya.service import v2


class ZookeeperConfig(v2.AryaConfig):
    list_display = ['ip','port','zk_tag','start_user']
    # show_add = True
v2.site.register(models.Zookeeper, ZookeeperConfig)

class KafkaConfig(v2.AryaConfig):
    list_display = ['ip','port','kafka_tag','start_user']
    # show_add = True
v2.site.register(models.Kafka, KafkaConfig)


class OssConfig(v2.AryaConfig):
    def _login(self,row=None,is_title=None):
        if is_title:
            return '登录'
        ret = models.Oss.objects.filter(pk=row.id).first()
        try:
            str = '<a href="/arya/rbac/alicloud/list.html?q={0}">{1}</a>'
            str_none = '<a>{0}</a>'
            # 判断 是否有查看用户的权限
            if '/arya/rbac/alicloud/list.html' in (item['url'] for item in
                                        self.site.request.session.get(settings.PERMISSION_AUTH_KEY)):
                reslut=str.format(ret.login,ret.login)
            else:
                reslut = str_none.format(ret.login)
            return mark_safe(reslut)
        except AttributeError:
            return ''

    def backetname(self,row=None,is_title=None):
        if is_title:
            return 'BackentName'
        value_list = models.Oss.objects.filter(pk=row.id).values('backetname__name')
        str = '<a href="/arya/rbac/backetname/list.html?q={0}">{1}</a>'

        ret=''
        for value in value_list:
            html=str.format(value['backetname__name'],value['backetname__name'])
            ret=ret+html
        return mark_safe(ret)

    def oss_auth(self,row=None,is_title=None):
        if is_title:
            return '权限'
        ret = models.BacketName.objects.filter(name=row.backetname.first()).first().get_ossauth_display()
        return ret

    list_display = [_login,backetname,'oss_tag',oss_auth]

v2.site.register(models.Oss, OssConfig)



class BacketNameConfig(v2.AryaConfig):
    def oss_auth(self,row=None,is_title=None):
        if is_title:
            return '权限'
        ret = models.BacketName.objects.filter(pk=row.id).first().get_ossauth_display()
        return ret

    list_display = ['name',oss_auth]
    search_list = ['name', ]
v2.site.register(models.BacketName, BacketNameConfig)



class ConsumerConfig(v2.AryaConfig):
    list_display = ['title']
    search_list = ['title', ]
v2.site.register(models.Consumer, ConsumerConfig)


class ProducerConfig(v2.AryaConfig):
    list_display = ['title']
    search_list = ['title', ]
v2.site.register(models.Producer, ProducerConfig)


class TopicConfig(v2.AryaConfig):
    def producer(self,row=None,is_title=None):
        if is_title:
            return '生产者'
        producer_list=models.Topic.objects.filter(pk=row.id).values('producer__title')
        ret=''
        str = '<a href="/arya/rbac/producer/list.html?q={0}">{1}</a>'
        for producer_value in producer_list:
            html=str.format(producer_value['producer__title'],producer_value['producer__title'])
            ret=ret+html
        return  mark_safe(ret)


    def consumer(self,row=None,is_title=None):
        if is_title:
            return '消费者'
        consumer_list = models.Topic.objects.filter(pk=row.id).values('consumer__title')
        ret = ''
        str = '<a href="/arya/rbac/consumer/list.html?q={0}">{1}</a>'
        for consumer_value in consumer_list:
            html=str.format(consumer_value['consumer__title'],consumer_value['consumer__title'])
            ret = ret + html
        return mark_safe(ret)


    list_display = ['title',producer,consumer]
    search_list = ['title', ]
v2.site.register(models.Topic, TopicConfig)



class MqCaseConfig(v2.AryaConfig):
    list_display = ['url','name','region']
    search_list = ['url', ]
v2.site.register(models.MqCase, MqCaseConfig)



class RabbitMQConfig(v2.AryaConfig):
    def case(self,row=None,is_title=None):
        if is_title:
            return 'RabbitMQ实例'
        ret= models.RabbitMQ.objects.filter(pk=row.id).first()
        str = '<a href="/arya/rbac/mqcase/list.html?q={0}">{1}</a>'
        reslut = str.format(ret.case, ret.case)
        return mark_safe(reslut)

    def mq_login(self,row=None,is_title=None):
        if is_title:
            return '登录'
        ret = models.RabbitMQ.objects.filter(pk=row.id).first()
        str = '<a href="/arya/rbac/alicloud/list.html?q={0}">{1}</a>'
        reslut = str.format(ret.mq_login, ret.mq_login)
        return mark_safe(reslut)



    def topic(self,row=None,is_title=None):
        if is_title:
            return 'topic'
        val_list=models.RabbitMQ.objects.filter(pk=row.id).values('topic__title')
        str = '<a href="/arya/rbac/topic/list.html?q={0}">{1}</a>'
        ret=''
        for value in val_list:
            html=str.format(value['topic__title'],value['topic__title'])
            ret=ret+html
        return  mark_safe(ret)


    list_display = [case,mq_login,topic,]
    search_list = ['case', ]
v2.site.register(models.RabbitMQ, RabbitMQConfig)



class RedisConfig(v2.AryaConfig):
    def password_base(self,row=None,is_title=None):
        if is_title:
            return '登录密码'
        obj=models.Redis.objects.filter(pk=row.id).first()

        ret=jiami_class.jiami().base_str_decrypt(obj.password)

        return ret

    def get_list_display(self,request):
        result=[]
        show_pwd=self.aget.get_show_add(request)
        if show_pwd:
            result.extend(self.list_display)
        else:
            result.extend(self.list_display_nopwd)
        # 如果有查看详情权限
        if self._remarks:
            if 'remarks' in request.permission_code_list:
                result.append(self.basic.remarks_view)
        # 如果有编辑权限
        # if True:
        if self._edit:
            if 'edit' in request.permission_code_list:
                # result.append(AryaConfig.change_view)
                result.append(self.basic.change_view)
        # 如果有删除权限
        # if True:
        if self._del:
            if 'del' in request.permission_code_list:
                result.append(self.basic.delete_view)
        result.insert(0, self.basic.checkbox_view)
        return result

    list_display = ['redis_tag','url',password_base]
    list_display_nopwd = ['redis_tag','url']

    def add(self,req):
        '''
        传递self对象
        传递req
        传递 加密解密的 在前段页面中的关键字
        '''
        ret=arya_func.core_add(self,req,'password')
        self._log_in_db(req, url=self.add_log_url,
                proj=self.mod, action='add', msg='add_' + self.mod)
        return ret


    def change(self,req,nid):
        '''
        传递self对象
        传递req
        传递被修改者id
        传递 加密解密的 在前段页面中的关键字
        '''
        ret=arya_func.core_change(self,req,nid,'password')
        self._log_in_db(req, url=self.update_log_url,
                    proj=self.mod, action='update', msg='update_' + self.mod)
        return ret
v2.site.register(models.Redis, RedisConfig)



class MysqlLoginConfig(v2.AryaConfig):

    def get_model_form(self):
        if self.model_f:
            return self.model_f
        class Dynamic(ModelForm):
            class Meta:
                model=models.MysqlLogin
                fields='__all__'
                widgets = {
                    'remarks':widgets.TextInput(attrs={'class': 'done','disabled ':'true'}),
                    'mysqlauth':widgets.Select(attrs={'class': 'done','disabled ':'true'}),
                    'database':widgets.SelectMultiple(attrs={'class': 'done','disabled ':'true'}),
                }

        return Dynamic


    def mysql_auth(self,row=None,is_title=None):
        if is_title:
            return 'mysql授权'
        ret = models.MysqlLogin.objects.filter(pk=row.id).first().get_mysqlauth_display()
        return ret

    def password_base(self,row=None,is_title=None):
        if is_title:
            return '密码'
        obj=models.MysqlLogin.objects.filter(pk=row.id).first()
        ret=jiami_class.jiami().base_str_decrypt(obj.password)
        return ret


    def database(self,row=None,is_title=None):
        if is_title:
            return '库'
        ret = ''
        str = '<a href="/arya/rbac/database/list.html?q={0}">{1}</a>'
        obj=models.MysqlLogin.objects.filter(pk=row.id).first().database.all()
        for database_obj in obj:
            html = str.format(database_obj.name, database_obj.name)
            ret = ret + html
        return mark_safe(ret)


    def mysql(self,row=None,is_title=None):
        if is_title:
            return '实例'
        ret = ''
        str = '<a href="/arya/rbac/mysql/list.html?q={0}">{1}</a>'
        obj=models.MysqlLogin.objects.filter(pk=row.id).first().database.all()
        for database_obj in obj:
            html = str.format(database_obj.databases, database_obj.databases)
            ret = ret + html
        return mark_safe(ret)

    def add(self,req):
        '''
        传递self对象
        传递req
        传递 加密解密的 在前段页面中的关键字
        '''
        ret=arya_func.core_add(self,req,'password')
        self._log_in_db(req, url=self.add_log_url,
                proj=self.mod, action='add', msg='add_' + self.mod)
        return ret


    def change(self,req,nid):
        '''
        传递self对象
        传递req
        传递被修改者id
        传递 加密解密的 在前段页面中的关键字
        '''
        ret=arya_func.core_change(self,req,nid,'password')
        self._log_in_db(req, url=self.update_log_url,
                proj=self.mod, action='update', msg='update_' + self.mod)
        return ret
    list_display = [mysql,database,'username',password_base,mysql_auth]
    search_list = ['username', ]
v2.site.register(models.MysqlLogin, MysqlLoginConfig)


class DataBaseConfig(v2.AryaConfig):
    def mysqllogin(self,row=None,is_title=None):
        if is_title:
            return '用户'
        ret = ''
        str = '<a href="/arya/rbac/mysqllogin/list.html?q={0}">{1}</a>'
        str_done = '<a href="/arya/rbac/mysqllogin/list.html?q={0}" class="strdone">{1}</a>'
        str_none = '<a>{0}</a>'
        str_none_done = '<a class="strdone">{0}</a>'
        i=0
        obj = models.DataBase.objects.filter(pk=row.id).first().logindatabase.all()
        for login_obj in obj:
            # 判断 是否有查看用户的权限
            if '/arya/rbac/mysqllogin/list.html' in (item['url'] for item in
                                              self.site.request.session.get(settings.PERMISSION_AUTH_KEY)):
                if i<5:
                    html = str.format(login_obj.username, login_obj.username)
                    i+=1
                else:
                    html = str_done.format(login_obj.username, login_obj.username)
            else:
                if i<5:
                    html = str_none.format(login_obj.username)
                    i+=1
                else:
                    html = str_none_done.format(login_obj.username)
            ret = ret + html
        return mark_safe(ret)


    list_display = [ 'databases','name', mysqllogin]
    search_list = ['name', ]

v2.site.register(models.DataBase, DataBaseConfig)


class MysqlConfig(v2.AryaConfig):
    show_ali=True
    show_all_data=True
    def mysql_login(self,row=None,is_title=None):
        if is_title:
            return '数据库用户'
        ret = ''
        str = '<a href="/arya/rbac/mysqllogin/list.html?q={0}">{1}</a>'
        str_done = '<a href="/arya/rbac/mysqllogin/list.html?q={0}" class="strdone">{1}</a>'
        str_none='<a>{0}</a>'
        str_none_done='<a class="strdone">{0}</a>'
        database_list = models.Mysql.objects.filter(pk=row.id).first().databasecase.all()
        i=0
        for database in database_list:
            for data_obj in database.logindatabase.all():
                #判断 是否有查看用户的权限
                if '/arya/rbac/mysqllogin/list.html' in (item['url'] for item in
                                              self.site.request.session.get(settings.PERMISSION_AUTH_KEY)):
                    if i<5:
                        html = str.format(data_obj.username, data_obj.username)
                        i += 1
                    else:
                        html=str_done.format(data_obj.username,data_obj.username)

                else:
                    if i <5:
                        html=str_none.format(data_obj.username)
                        i+=1
                    else:
                        html=str_none_done.format(data_obj.username)
                ret = ret + html
            # yield ret
        return mark_safe(ret)

    def database(self,row=None,is_title=None):
        if is_title:
            return '库'
        obj = models.Mysql.objects.filter(pk=row.id).first()
        str = '<a href="/arya/rbac/database/list.html?q={0}">{1}</a>'
        str_done = '<a href="/arya/rbac/database/list.html?q={0}" class="strdone" >{1}</a>'
        ret = ''
        i=0
        for item in obj.databasecase.all():
            if i<5:
                ret += str.format(item.name, item.name)
                i+=1
            else:
                ret += str_done.format(item.name, item.name)
        return mark_safe(ret)

    list_display = ['name','url',database,mysql_login,'cpu','memory','iops','maxconnet']
    # list_display = [case,mysql_login,database,type,'port',]
v2.site.register(models.Mysql, MysqlConfig)



class ALiCloudConfig(v2.AryaConfig):
    def password_base(self,row=None,is_title=None):
        if is_title:
            return '密码'
        obj=models.ALiCloud.objects.filter(pk=row.id).first()
        ret=jiami_class.jiami().base_str_decrypt(obj.password)
        return ret

    def accesskey_base(self,row=None,is_title=None):
        if is_title:
            return 'accesskey'
        obj=models.ALiCloud.objects.filter(pk=row.id).first()
        ret=jiami_class.jiami().base_str_decrypt(obj.accesskey_id)
        return ret

    def accesskeysecret_base(self,row=None,is_title=None):
        if is_title:
            return 'accesskeysecret'
        obj=models.ALiCloud.objects.filter(pk=row.id).first()
        ret=jiami_class.jiami().base_str_decrypt(obj.accesskeysecret)
        return ret

    def add(self,req):
        '''
        传递self对象
        传递req
        传递 加密解密的 在前段页面中的关键字
        '''
        ret=arya_func.core_add(self,req,['password','accesskey_id','accesskeysecret'])
        self._log_in_db(req, url=self.add_log_url,
                    proj=self.mod, action='add', msg='add_' + self.mod)

        return ret


    def change(self,req,nid):
        '''
        传递self对象
        传递req
        传递被修改者id
        传递 加密解密的 在前段页面中的关键字
        '''
        ret=arya_func.core_change(self,req,nid,['password','accesskey_id','accesskeysecret'])
        self._log_in_db(req, url=self.update_log_url,
                    proj=self.mod, action='update', msg='update_' + self.mod)
        return ret
    list_display = ['username',accesskey_base,accesskeysecret_base]
    search_list = ['username', ]
v2.site.register(models.ALiCloud, ALiCloudConfig)


class FtpConfig(v2.AryaConfig):
    list_display = ['username','password','path']
    # show_add = True
v2.site.register(models.Ftp, FtpConfig)

class SvnConfig(v2.AryaConfig):
    def svn_auth(self,row=None,is_title=None):
        if is_title:
            return '权限'
        ret = models.Svn.objects.filter(pk=row.id).first().get_svnauth_display()
        return ret
    list_display = ['path',svn_auth]
v2.site.register(models.Svn, SvnConfig)



class SvnGroupConfig(v2.AryaConfig):
    list_display = ['username','password']
    # show_add = True
v2.site.register(models.SvnGroup, SvnGroupConfig)



