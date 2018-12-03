from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.db.models import Q

from arya.service import v2
from . import models
from utlis import arya_func

class UserConfig(v2.AryaConfig):
    list_display = ['name',]
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


    # show_add=True
v2.site.register(models.User, UserConfig)


class PermissionConfig(v2.AryaConfig):
    list_display = ['name','url','menu_gp','code','group']
    # show_add=True
v2.site.register(models.Permission, PermissionConfig)

class GroupConfig(v2.AryaConfig):
    list_display = ['name',]
    # show_add=True
v2.site.register(models.Group, GroupConfig)

class MenuConfig(v2.AryaConfig):
    list_display = ['name',]
    # show_add=True
v2.site.register(models.Menu, MenuConfig)


class PteamPermissionConfig(v2.AryaConfig):
    list_display = ['name',]
    # show_add=True
v2.site.register(models.PteamPermission, PteamPermissionConfig)

class PteamConfig(v2.AryaConfig):
    list_display = ['name','groupname']
    # show_add=True
v2.site.register(models.Pteam, PteamConfig)



class OperationLogConfig(v2.AryaConfig):
    def remarks_view(self,row=None,is_title=None):
        if is_title:
            return '日志'
        _str='arya:%s_%s_remarks' %(self.app,self.mod)
        url=reverse(viewname=_str,args=(row.id,))
        result='<a href="{0}" class="btn btn-info">tail -f</a>'.format(url)
        return mark_safe(result)

    def remarks(self,req,nid):
        get_num=req.GET.get('num')
        get_line=req.GET.get('line')
        ret_li = []
        if not get_num:
            if get_line:
                if get_line !='No_Robot':
                    get_line=int(get_line)
                    obj_li = models.OperationLog.objects.all().order_by('-id')[:get_line]
                else:
                    obj_li = models.OperationLog.objects.filter(~Q(user_id=27)).order_by('-id')
                # obj_li = models.OperationLog.objects.all()[:get_line].order_by('-id')
            else:
                obj_li = models.OperationLog.objects.all().order_by('-id')
            for obj in obj_li:
                ct=str(obj.ctime).split('.')[0]
                ret_str='<div class="log_remark">'
                try:
                    ret_str+='<span style="color: red">{0}  </span>'.format(obj.user.name)
                except AttributeError:
                    ret_str += '<span style="color: red"> </span>'
                ret_str+='操作时间:'
                ret_str+='<span style="color: red">{0}  </span> '.format(ct)
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
        #这里就不记录日志了
        return render(req, 'log/remarks.html', locals())


    def ctime(self,row=None,is_title=None):
        if is_title:
            return '访问时间'
        obj=models.OperationLog.objects.filter(pk=row.id).first()
        return obj.ctime

    list_display = ['user',ctime,'url','proj','action','explain']
    # show_add=True
v2.site.register(models.OperationLog, OperationLogConfig)
