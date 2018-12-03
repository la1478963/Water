import requests
import json
import threading
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.db import transaction
from django.shortcuts import render,HttpResponse,redirect
from celery.result import AsyncResult
from CMDB.celery import app

from client.bin.run import JG_info
from rbac import models
from client import t_ali,t_ali_rds
from django.conf import settings
from utlis.log_class import Logger
from utlis.jiami_class import jiami
from clientapi.task import ali_func,alirds_func
from app01.task import add,mul,log_indb

def db_func(req):
    new='Vq5^KYt70SM35tyB%Gi4'
    base_new=jiami().base_str_encrypt(new)
    # obj_l=models.Login.objects.filter(login_name='root',login_pwd=base_s)
    num=models.Login.objects.filter(
        login_name='readonly',login_pwd='S1l0NzBTTTM1dHlCJUdpNHdlITQ1OEBF'
                                    ).update(login_pwd=base_new)
    return HttpResponse(num)



@csrf_exempt
def ali_ret_api(req):
    ret_str = req.body.decode()
    ret_data_dic = json.loads(ret_str)
    for host,value in ret_data_dic.items():
        tag = False
        os = value.get('ostype', '')
        ali_id=host
        sn=value.get('sn','')
        hostname=value.get('hostname','')
        mem=value.get('mem','')
        status=value.get('status','')
        starttime=value.get('starttime','')
        stoptime=value.get('stoptime','')
        eth1=value.get('eth1','')
        eth0=value.get('eth0','')
        kernel=value.get('osname','')
        cpu=value.get('cpu','')
        vpnnet=value.get('vpc_net','')
        vswitch=value.get('vswitch','')
        vpccon_li=value.get('vpc_con','')
        speed=value.get('speed','')
        if value.get('disk'):
            disk=[]
            for item in value['disk']:
                disk.append({item['route']:item['size']})
                # disk_size.append(item['size'])
                # disk_route.append(item['route'])
            tag=True

        os_obj=models.Os.objects.filter(name=os).first()
        if not os_obj:
            os_obj=models.Os.objects.create(name=os)

        vpcnet_obj=models.VpcNet.objects.filter(title=vpnnet).first()
        if not vpcnet_obj:
            vpcnet_obj=models.VpcNet.objects.create(title=vpnnet)

        vpcsw_obj = models.VpcSwitch.objects.filter(title=vswitch).first()
        if not vpcsw_obj:
            vpcsw_obj = models.VpcSwitch.objects.create(title=vswitch)
        if vpccon_li:
            vpccon_val = models.VpcNet.objects.filter(title=vpccon_li[0]).first().id
        else:
            vpccon_val=None

        if tag:
            disk_l=[]
            for i in disk:
                for k,v in i.items():
                    disk_obj=models.Disk.objects.filter(path=k,size=v).first()
                    if not disk_obj:
                        disk_obj=models.Disk.objects.create(path=k,size=v)
                    disk_l.append(disk_obj)

        host_obj=models.Host.objects.filter(ecsname=ali_id)
        if not host_obj.first():
            with transaction.atomic():
                host_obj=models.Host.objects.create(
                    hostname=hostname,
                    ecsname=ali_id,
                    cpu=cpu,
                    mem=mem,
                    speed=speed,
                    eth1_network=eth1,
                    eth0_network=eth0,
                    sn=sn,
                    kernel=kernel,
                    createtime=starttime,
                    expirytime=stoptime,
                    state=1,
                    os=os_obj,
                    vpcnet=vpcnet_obj,
                    vpcsw=vpcsw_obj,
                    vpccon_id=vpccon_val,
                )
                if tag:
                    for disk_obj in disk_l:
                        try:
                            host_obj.disks.add(*disk_obj)
                        except TypeError:
                            host_obj.disks.add(disk_obj)
        else:
            with transaction.atomic():
                host_obj.update(
                    hostname=hostname,
                    ecsname=ali_id,
                    cpu=cpu,
                    mem=mem,
                    speed=speed,
                    eth1_network=eth1,
                    eth0_network=eth0,
                    sn=sn,
                    kernel=kernel,
                    createtime=starttime,
                    expirytime=stoptime,
                    state=1,
                    os=os_obj,
                    vpcnet=vpcnet_obj,
                    vpcsw=vpcsw_obj,
                    vpccon_id=vpccon_val,
                )
                if tag:
                    host_obj.first().disks.clear()
                    for disk_obj in disk_l:
                        try:
                            host_obj.first().disks.add(*disk_obj)
                        except TypeError:
                            host_obj.first().disks.add(disk_obj)
    return HttpResponse('ok')


#调用请求阿里云api主接口
@csrf_exempt
def ali_main(req):
    import json
    source_url=req.META.get('HTTP_REFERER', '/')
    if 'host' in source_url:
        ali_func.delay()

        #调用 celery 写入日志
        log_indb.delay(req.session.get(settings.USERID),
                       '/arya/ali_main.html/', explain='ali_host', msg='ali_host')
        # print('ali_func------',ret.id)
        return redirect(source_url)

    elif 'mysql' in source_url:
        alirds_func.delay()

        #调用celery 写入日志
        log_indb.delay(req.session.get(settings.USERID),
                       '/arya/ali_main.html/', explain='ali_rds', msg='ali_rds')
        return redirect(source_url)
    else:
        return HttpResponse('无')


@csrf_exempt
def alirds_ret_api(req):
    logger = Logger(loglevel=1, logger="fox").getlog()
    case_list=req.body.decode()
    case_list=json.loads(case_list)
    for case in case_list:
        for item in case.values():
            try:
                mysqlcase_obj_li=mysqlcase(item)
            except KeyError:
                print('------',item)
                print('======',case)
            t = threading.Thread(target=mysqldatabase,args=(mysqlcase_obj_li,item))
            t.start()
    return HttpResponse('ok')


def mysqlcase(item):
    url = item['url']
    cpu = item['cpu']
    mem = item['mem'] // 1024
    maxcon = item['maxcon']
    iops = item['iops']
    disk = item['disk']
    use_disk = item['use_disk']
    types = item['type']
    master = item.get('master', '')
    caseid = item['caseid']
    hostname = item['hostname']
    db_li = item['db']
    #mysql实例
    mysqlcase_obj = models.Mysql.objects.filter(hostname=caseid)
    if not mysqlcase_obj.first():
        models.Mysql.objects.create(
            url=url, name=hostname, hostname=caseid, type=types, cpu=cpu,
            memory=mem, iops=iops, maxconnet=maxcon, maxstorage=disk,
            usestorage=use_disk
        )

    else:
        mysqlcase_obj2 = models.Mysql.objects.filter(
            url=url, name=hostname, hostname=caseid, type=types, cpu=cpu,
            memory=mem, iops=iops, maxconnet=maxcon, maxstorage=disk,
            usestorage=use_disk
        )
        if not mysqlcase_obj2.first():
            mysqlcase_obj.update(url=url, name=hostname, hostname=caseid, type=types, cpu=cpu,
            memory=mem, iops=iops, maxconnet=maxcon, maxstorage=disk,usestorage=use_disk)

    mysqlcase_obj_li = models.Mysql.objects.filter(
        url=url, name=hostname, hostname=caseid, type=types, cpu=cpu,
        memory=mem, iops=iops, maxconnet=maxcon, maxstorage=disk,
        usestorage=use_disk)
    return mysqlcase_obj_li


def mysqldatabase(mysqlcase_obj_li,item):
    logger = Logger(loglevel=1, logger="fox").getlog()
    db_li = item['db']
    #mysql库
    for mysqlcase_obj in mysqlcase_obj_li:
        for db in db_li:
            for db_name,value in db.items():
                db_obj=models.DataBase.objects.filter(name=db_name,databases=mysqlcase_obj)
                if not db_obj.first():
                    models.DataBase.objects.create(name=db_name,
                                        databases=mysqlcase_obj)
                    db_obj = models.DataBase.objects.filter(name=db_name, databases=mysqlcase_obj)
                dblogin(db_obj,item, value)


def dblogin(db_obj,item,value):
    auth_dic = {
        'ReadOnly': 1,
        'ReadWrite': 2,
    }
    for db_login_item in value['user']:
        username = db_login_item[0]
        userauth = db_login_item[1]
        mysql_login_obj=models.MysqlLogin.objects.filter(username=username,
                mysqlauth = auth_dic[userauth],database=db_obj)
        if not mysql_login_obj.first():
            with transaction.atomic():
                mysql_login_obj=models.MysqlLogin.objects.create(username=username,
                                     mysqlauth=auth_dic[userauth],
                                             )
                for db_item in db_obj:
                    try:
                        mysql_login_obj.database.add(*db_item)
                    except TypeError:
                        mysql_login_obj.database.add(db_item)
        else:
            pass
            # print('正常')



def celery_status(req):
    import datetime
    import json
    if req.method=='GET':
        if req.GET.get('x') and req.GET.get('y'):
            # 立即执行
            # ret=add.delay(int(req.GET.get('x')),int(req.GET.get('y')))
            if req.GET.get('after'):
                ctime = datetime.datetime.now()
                utc_ctime = datetime.datetime.utcfromtimestamp(ctime.timestamp())
                s1 = datetime.timedelta(seconds=int(req.GET.get('after'))*60)
                ctime_x = utc_ctime + s1
                # 使用apply_async并设定时间
            year=req.GET.get('year')
            mouth=req.GET.get('month')
            day=req.GET.get('day')
            hour=req.GET.get('hour')
            minute=req.GET.get('minute')
            if year and mouth and day and hour and minute:
                ctime = datetime.datetime(year=int(year), month=int(mouth),
                                  day=int(day), hour=int(hour), minute=int(minute))
                # 把当前本地时间转换成UTC时间
                ctime_x = datetime.datetime.utcfromtimestamp(ctime.timestamp())
            if ctime_x:
                ret = add.apply_async(args=[int(req.GET.get('x')), int(req.GET.get('y'))], eta=ctime_x)
                num=ret.id
        if req.GET.get('cancel'):

            async = AsyncResult(id=req.GET.get('cancel'), app=app)
            async.revoke(terminate=True)
            cancel_tag='取消成功'
        if req.GET.get('stop'):
            async = AsyncResult(id=req.GET.get('stop'), app=app)
            async.revoke()
            stop_tag='中止成功'
        return render(req,'celery.html',locals())
    else:
        ret=req.POST.get('id','')
        data = ''
        if ret:
            async=AsyncResult(id=ret,app=ali_func)
            if async.successful():
                data='执行成功,数据是:'+str(async.get())
                async.forget()
            elif async.failed():
                data='执行失败'
            elif async.status=='PENDING':
                data='等待被执行'
            elif async.status=='RETPY':
                data='任务异常正在重试'
            elif async.status=='STARTED':
                data='任务正在执行'
            else:
                data='未知'
        return render(req,'celery.html',locals())




#调用salt_api执行
@csrf_exempt
def client_func(req,):
    #执行开始
    JG_func=JG_info._begin()
    if JG_func =='ok':
        return HttpResponse('更新成功')
    else:
        return HttpResponse('更新失败')

#给CMDB的api,提供给 salt 入库
# @csrf_exempt
# def ret_salt_api(req,):
#     ret_str=req.body.decode()
#     ret_data_dic=json.loads(ret_str)
#     for host,value in ret_data_dic.items():
#         if 'cpu' not in value.keys():
#             # print('error',host,value)
#             continue
#         cpu_obj=models.Cpu.objects.filter(
#             cpuarch=value['cpu']['cpuarch'],
#             num_cpus=value['cpu']['num_cpus'],
#             cpu_model=value['cpu']['cpu_model'],
#         ).first()
#         if not cpu_obj:
#             cpu_obj = models.Cpu.objects.create(
#                 cpuarch=value['cpu']['cpuarch'],
#                 num_cpus=value['cpu']['num_cpus'],
#                 cpu_model=value['cpu']['cpu_model'],
#             )
#         motherboard_obj=models.Motherboard.objects.filter(
#             sn=value['motherboard']['Serial Number'],
#             manufacturer=value['motherboard']['Manufacturer'],
#             pn=value['motherboard']['Product Name']
#         ).first()
#         if not motherboard_obj:
#             motherboard_obj = models.Motherboard.objects.create(
#                 sn=value['motherboard']['Serial Number'],
#                 manufacturer=value['motherboard']['Manufacturer'],
#                 pn=value['motherboard']['Product Name']
#             )
#
#
#         mem_obj=models.Memory.objects.filter(
#             size=value['mem']['Size'],
#             width=value['mem']['Data Width'],
#             locator=value['mem']['Locator'],
#             type=value['mem']['Type'],
#         ).first()
#         if not mem_obj:
#             mem_obj = models.Memory.objects.create(
#                 size=value['mem']['Size'],
#                 width=value['mem']['Data Width'],
#                 locator=value['mem']['Locator'],
#                 type=value['mem']['Type'],
#             )
#
#         eth1_obj=models.Network.objects.filter(
#             ip_address=value['network']['eth1'][0],
#             mac_address=value['network']['eth1'][1],
#         ).first()
#         if not eth1_obj:
#             eth1_obj = models.Network.objects.create(
#                 ip_address=value['network']['eth1'][0],
#                 mac_address=value['network']['eth1'][1],
#             )
#
#         eth0_obj=models.Network.objects.filter(
#             ip_address=value['network']['eth0'][0],
#             mac_address=value['network']['eth0'][1],
#         ).first()
#         if not eth0_obj:
#             eth0_obj = models.Network.objects.create(
#                 ip_address=value['network']['eth0'][0],
#                 mac_address=value['network']['eth0'][1],
#             )
#         os_obj=models.Os.objects.filter(name=value['other']['os']).first()
#         if not os_obj:
#             os_obj = models.Os.objects.create(name=value['other']['os'])
#         osarch_obj=models.Osarch.objects.filter(sarch=value['other']['osarch'],).first()
#         if not osarch_obj:
#             osarch_obj = models.Osarch.objects.create(sarch=value['other']['osarch'])
#
#         disk_obj_li=[]
#         for item in value['disk'].keys():
#             disk_obj=models.Disk.objects.filter(path=item,size=value['disk'][item]).first()
#             if not disk_obj:
#                 disk_obj = models.Disk.objects.create(path=item,size=value['disk'][item])
#             disk_obj_li.append(disk_obj)
#
#         obj = models.Host.objects.filter(hostname=host)
#         if obj.first():
#             with transaction.atomic():
#                 obj.update(
#                     hostname=host,
#                     login_port=value['port'],
#                     cpu=cpu_obj,
#                     motherboard=motherboard_obj,
#                     mem=mem_obj,
#                     eth1_network=eth1_obj,
#                     eth0_network=eth0_obj,
#                     uuid=value['other']['uuid'],
#                     os=os_obj,
#                     osarch=osarch_obj,
#                     kernel=value['other']['kernel'],
#                 )
#                 obj.first().disk.clear()
#                 obj.first().disk.add(*disk_obj_li)
#         else:
#             with transaction.atomic():
#                 obj=models.Host.objects.create(
#                     hostname=host,
#                     login_port=value['port'],
#                     cpu=cpu_obj,
#                     motherboard=motherboard_obj,
#                     mem=mem_obj,
#                     eth1_network=eth1_obj,
#                     eth0_network=eth0_obj,
#                     uuid=value['other']['uuid'],
#                     os=os_obj,
#                     osarch=osarch_obj,
#                     kernel=value['other']['kernel'],
#                 )
#                 obj.disk.add(*disk_obj_li)
#     return HttpResponse('ok')
