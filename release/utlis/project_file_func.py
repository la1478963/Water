import os,time
from rbac import models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Data_Processing(object):
    def __init__(self,nid):
        self.nid=nid
    def func_file_li(self,file_li):
        ret_li=[]
        if not isinstance(file_li,list):
            print(file_li)
            raise TypeError
        if file_li:
            for package in file_li:
                package_name=package.name
                #上传文件 ，本来应该上传 到oss的
                package_path=os.path.join(BASE_DIR, "file\\"+package_name)
                with open(package_path,'wb+') as w:
                    for chunk in package.chunks():
                        w.write(chunk)
                t = package_name.rsplit('.')[-1]
                for i in models.Package.packagetype_choices:
                    if t == i[1]:
                        num = i[0]
                        break
                self.model_func(package_name,package_path,num)

    def model_func(self,package_name,package_path,num):
        models.Package.objects.create(proj_id=int(self.nid), disname=package_name,
                                      osspath=package_path, ctime=time.time(),
                                      type=num
                                      )
