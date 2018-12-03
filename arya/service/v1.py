import copy
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
# from django.urls import reverse
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from rbac import models
from django.conf.urls import url,include
from django.db.models import Q
from ..utils.page import Pagination

from rbac.views import init
from django.conf import settings
# from clientapi.views import ret_salt_api
# from clientapi.views import client_func
# from keras.models import load_model
from clientapi import views
from app01.task import log_indb



class ChangeList(object):
        #data=ChangeList(self,queryset)
    def __init__(self,site,queryset):
        self.model_class=site.model_class
        self.get_list_display=site.get_list_display(site.request)
        self.site=site
        self.get_show_ali=site.get_show_ali(site.request)
        self.get_show_all_data=site.get_show_all_data(site.request)
        self.get_show_add=site.get_show_add(site.request)
        self.get_show_dels=site.get_show_dels(site.request)
        self.add_url=site.add_url
        self.get_search_list=site.get_search_list
        self.get_accurate_list=site.get_accurate_list
        self.get_search_button=site.get_search_button
        self.get_q=site.request.GET.get('q','')
        self.pteamrole=site.request.GET.get('pteamrole','')
        self.ab=site.request.GET.get('ab','')
        self.environment=site.request.GET.get('environment','')


        # par_page=site.par_page
        page_count=site.page_count
        request=site.request
        query_get=copy.deepcopy(request.GET)
        #获取页码
        request_page=site.request.GET.get('page','1')
        #获取每页显示多少条信息
        par_page = int(site.request.GET.get('page_list', '10'))
        all_count=queryset.count()
        page_url=site.list_url
        pag_obj=Pagination(request_page,all_count,page_url,query_get,par_page,page_count)
        self.queryset=queryset[pag_obj.start:pag_obj.end]
        self.page_html=pag_obj.page_html()
        self.page_list_html=pag_obj.page_list_html()


    def table_head(self):
        result = []
        for item in self.get_list_display:
            if isinstance(item,str):
                temp=self.model_class._meta.get_field(item).verbose_name
            else:
                temp=item(self.site,is_title=True)
            result.append(temp)
        return result


    def table_body(self):
        result=[]
        for obj in self.queryset:
            ret=[]
            for item in self.get_list_display:
                if isinstance(item,str):
                    temp=getattr(obj,item)
                else:
                    try:
                        temp = item(row=obj)
                    except TypeError:
                        temp = item(self.site,row=obj)
                        #         temp=item(self,row=obj)
                ret.append(temp)
            result.append(ret)
        return result


class AryaConfig(object):
    def __init__(self,model_class,site):
        self.model_class=model_class
        self.app=self.model_class._meta.app_label
        self.mod=self.model_class._meta.model_name
        self.site=site
        self.list_log_url = '/arya/' + self.app + '/' + self.mod + '/list.html'
        self.remarks_log_url = '/arya/' + self.app + '/' + self.mod + '/remarks.html'
        self.add_log_url = '/arya/' + self.app + '/' + self.mod + '/add.html'
        self.update_log_url = '/arya/' + self.app + '/' + self.mod + '/update.html'
        self.delete_log_url = '/arya/' + self.app + '/' + self.mod + '/delete.html'
        # sf_model=load_model('model_v0.314_epoch-07-loss0.0742-valLoss0.1214.hdf5')
        # request.session['model']=sf_model
    _remarks=True
    _confpro=False
    _edit=True
    _add=True
    _del=True
    _dels = True
    show_ali=False
    show_all_data = False

    list_display=[]
    show_add=False
    show_dels=False
    model_f=False
    search_list=[]
    accurate_list=[]
    search_button_list=[]
    # par_page=10
    page_count=7

    @property
    def urls(self):
        parttents = [
            url('^$', self.list,name='%s_%s_list' %(self.app,self.mod)),
            url('list.html', self.list,name='%s_%s_list' %(self.app,self.mod)),
            url('^add.html', self.add,name='%s_%s_add' %(self.app,self.mod)),
            url('^(\d+)/delete.html', self.delete,name='%s_%s_del' %(self.app,self.mod)),
            url('^(\d+)/update.html', self.change,name='%s_%s_edit' %(self.app,self.mod)),
            url('^(\d+)/remarks.html', self.remarks,name='%s_%s_remarks' %(self.app,self.mod)),
        ]
        parttents+=self.gouzi()
        return parttents,None,None

    def gouzi(self):
        return []

    def get_show_ali(self,request):
        return self.show_ali

    def get_show_all_data(self,request):
        return self.show_all_data

    def get_show_add(self,request):
        if not self._add:
            return self.show_add
        if 'add' in request.permission_code_list:
        # if True:
            self.show_add=True
        return self.show_add

    def get_show_dels(self,request):
        if not self._dels:
            return self.show_dels
        if 'del' in request.permission_code_list:
        # if True:
            self.show_dels=True
        else:
            self.show_dels = False
        return self.show_dels

    def get_search_list(self):
        result=[]
        result.extend(self.search_list)
        return result

    def get_accurate_list(self):
        result = []
        result.extend(self.accurate_list)
        return result

    def get_search_button(self):
        result=[]
        try:
            JG_l = self.search_button_list()
            result.extend(JG_l)
        except TypeError:
            result.extend(self.search_button_list)
        return result

    def get_list_display(self,request):
        result=[]
        result.extend(self.list_display)

        # 如果有查看详情权限
        # if self._confpro:
        #     if 'confpro' in request.permission_code_list:
        #         result.append(self.configproj_view)

        #如果有查看备注权限
        if self._remarks:
            if 'remarks' in request.permission_code_list:
                result.append(self.remarks_view)

        # 如果有编辑权限
        # if True:
        if self._edit:
            if 'edit' in request.permission_code_list:
                # result.append(AryaConfig.change_view)
                result.append(self.change_view)
        # 如果有删除权限
        # if True:
        if self._del:
            if 'del' in request.permission_code_list:
                result.append(AryaConfig.delete_view)
        result.insert(0,AryaConfig.checkbox_view)
        return result

    def remarks_view(self,row=None,is_title=None):
        if is_title:
            return '备注'
        _str='arya:%s_%s_remarks' %(self.app,self.mod)
        url=reverse(viewname=_str,args=(row.id,))
        result='<a href="{0}" class="btn btn-info">查看备注</a>'.format(url)
        return mark_safe(result)

    def checkbox_view(self,row=None,is_title=None):
        if is_title:
            return ''
        result='<input type="checkbox" value={0}>'.format(row.id)
        return mark_safe(result)

    def change_view(self,row=None,is_title=None):
        if is_title:
            return '修改'
        _str='arya:%s_%s_edit' %(self.app,self.mod)
        url=reverse(viewname=_str,args=(row.id,))
        result='<a href="{0}" class="btn btn-warning">修改</a>'.format(url)
        return mark_safe(result)

    def delete_view(self,row=None,is_title=None):
        if is_title:
            return '删除'
        _str='arya:%s_%s_del' %(self.app,self.mod)
        url=reverse(viewname=_str,args=(row.id,))
        result='<a href="{0}" class="btn btn-danger">删除</a>'.format(url)
        return mark_safe(result)


    def get_model_form(self):
        if self.model_f:
            return self.model_f
        class Dynamic(ModelForm):
            class Meta:
                model=self.model_class
                fields='__all__'
        return Dynamic



    #调用celery  请求日志入库
    def _log_in_db(self,req,url,proj=None, action=None,explain=None,msg=None):
        log_indb(req.session.get(settings.USERID),
                 url, proj=proj, action=action, msg=msg)


    def list(self,req):
        self.request=req
        search_q=req.GET.get('q')
        candition_q=Q()
        search_list=self.get_search_list()
        if search_list and search_q:
            for search_item in search_list:
                temp_q=Q()
                temp_q.children.append((search_item,search_q))
                candition_q.add(temp_q,'OR')
        queryset=self.model_class.objects.filter(candition_q).order_by('-id')
        data=ChangeList(self,queryset)
        self._log_in_db(req,url=self.list_log_url, proj=self.mod,
                    action='list',msg='list_'+self.mod)

        return render(req,'list.html',{'data':data,'req':req})

    def remarks(self,req,nid):
        # dynamic_form = self.get_model_form()
        obj = self.model_class.objects.filter(id=nid)
        if req.method=='POST':
            remarks=req.POST.get('remarks')
            obj.update(remarks=remarks)
            return redirect(self.list_url)
        self._log_in_db(req, url=self.remarks_log_url,
                proj=self.mod, action='remarks', msg='remarks_'+self.mod)
        return render(req, 'remarks.html', locals())

    def add(self,req):
        dynamic_form=self.get_model_form()
        if req.method=='GET':
            form=dynamic_form()

            return render(req,'add.html',{'data':form,'req':req})
        else:
            form=dynamic_form(data=req.POST)
            if form.is_valid():
                form.save()
                self._log_in_db(req, url=self.add_log_url,
                        proj=self.mod, action='add', msg='add_' + self.mod)
                return redirect(self.list_url)
            return render(req, 'add.html', {'data': form,'req':req})

    def delete(self,req,nid):
        if req.method=='GET':
            return render(req,'del.html',{'req':req})
        else:
            obj=self.model_class.objects.filter(id=nid).delete()
            self._log_in_db(req, url=self.delete_log_url,
                    proj=self.mod, action='del', msg='del_'+self.mod)
            return redirect(self.list_url)


    def change(self,req,nid):
        dynamic_form = self.get_model_form()
        obj=self.model_class.objects.filter(id=nid).first()
        if req.method=='GET':
            form = dynamic_form(instance=obj)
            return render(req,'edit.html',{'data':form,'req':req})
        else:
            form = dynamic_form(instance=obj,data=req.POST)
            if form.is_valid():
                form.save()
                self._log_in_db(req, url=self.update_log_url,
                        proj=self.mod, action='update', msg='update_'+self.mod)
                return redirect(self.list_url)
            return render(req, 'edit.html', {'data': form,'req':req})


    @property
    def list_url(self):
        str='arya:%s_%s_list' %(self.app,self.mod)
        result=reverse(viewname=str)
        return result

    @property
    def del_url(self):
        str='arya:%s_%s_del' %(self.app,self.mod)
        result=reverse(viewname=str)
        return result

    @property
    def add_url(self):
        str = 'arya:%s_%s_add' % (self.app, self.mod)
        result = reverse(viewname=str)
        return result

class AryaSite(object):
    def __init__(self):
        self._registry={}


    def register(self,model_class,model_config):
                                    #实例化
        self._registry[model_class]=model_config(model_class,self)
        #用于 ali_func 的反向url
        # self.app = model_class._meta.app_label
        # self.mod = model_class._meta.model_name

    @property
    def urls(self):
        parttents=[
            url('^login/', init.login),
            url('^logout/', init.logout),
            url('^register/', init.register),
            url('^sendmail/', init.sendmail),
            url('^home/', init.home),
            url('^ali_client_api.html/', views.ali_ret_api ),
            url('^db_func.html/', views.db_func ),
            url('^ali_main.html/', views.ali_main ),
            url('^celery_status.html/', views.celery_status ),
            url('^alirds_client_api.html/', views.alirds_ret_api ),
        ]

        for model_class,model_config in self._registry.items():
            '''
            url("^db/host/" ([],None,None)),
            '''
            JG="^{0}/{1}/".format(model_class._meta.app_label,model_class._meta.model_name)
            pt=url(JG,model_config.urls)
            parttents.append(pt)
        return parttents
site=AryaSite()







