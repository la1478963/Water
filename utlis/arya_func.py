from rbac import models
from django.utils.safestring import mark_safe
# from django.urls import reverse
from django.core.urlresolvers import reverse
from django.conf.urls import url,include
from django.shortcuts import HttpResponse,render,redirect
import json
from utlis import jiami_class


def core_add(self, req,field):
    dynamic_form = self.get_model_form()
    if req.method == 'GET':
        form = dynamic_form()
        return render(req, 'add.html', {'data': form, 'req': req})
    else:
        req_dic = req.POST.dict()
        if isinstance(field,str):
            req_dic[field] = jiami_class.jiami().base_str_encrypt(req.POST[field])
        else:
            for item in field:
                req_dic[item]=jiami_class.jiami().base_str_encrypt(req.POST[item])
        form = dynamic_form(data=req_dic)
        if form.is_valid():
            form.save()
            # try:
            #     return redirect(self.list_url)
            # except AttributeError:
            return redirect(self.jump.list_url)
        return render(req, 'add.html', {'data': form, 'req': req})


def core_change(self, req, nid,field):
    dynamic_form = self.get_model_form()
    obj = self.model_class.objects.filter(id=nid).first()
    if req.method == 'GET':
        form = dynamic_form(instance=obj,initial={'pteams':obj.pteams.all()})

        if isinstance(field, str):
            base_str = jiami_class.jiami().base_str_decrypt(form[field].value())
            obj.__dict__[field]=base_str
        else:
            for item in field:
                base_str = jiami_class.jiami().base_str_decrypt(form[item].value())
                obj.__dict__[item]=base_str

        form = dynamic_form(instance=obj)
        if 'mysqllogin' in req.path_info:
            return render(req, 'edit.html', {'data': form, 'req': req,'tag':True})
        return render(req, 'edit.html', {'data': form, 'req': req})
    else:
        req_post=req.POST.copy()
        if isinstance(field, str):
            req_post[field] = jiami_class.jiami().base_str_encrypt(req.POST.get(field))
        else:
            for item in field:
                req_post[item] = jiami_class.jiami().base_str_encrypt(req.POST.get(item))

        database_list = req_post.getlist('database','')
        if database_list:
            req_post['database']=database_list
        form = dynamic_form(instance=obj, data=req_post)
        if form.is_valid():
            form.save()
            return redirect(self.jump.list_url)
        if 'mysqllogin' in req.path_info:
            return render(req, 'edit.html', {'data': form, 'req': req, 'tag': True})
        return render(req, 'edit.html', {'data': form, 'req': req})
