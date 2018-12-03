from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
import requests
import json
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeInstanceMonitorDataRequest
from aliyunsdkcore.profile import region_provider
from utlis.time_class import Time
from app01.task import log_indb
from client import t_ali,t_ali_rds
from rbac import models
from CMDB.celery import app

@app.task
def add(x, y):
    return x + y
@app.task
def mul(x, y):
    return x * y
@app.task
def xsum(numbers):
    return sum(numbers)



#调用阿里云获取监控数据
@shared_task
def ali_jiankong():
    start, end = Time().ali_def_monitor()
    clt = client.AcsClient('LTAIH9CwyQbfA0h3',
                           'lY8NnmUIFpfyYFXRs3IHVXhC2Ou6tZ',
                           'cn-beijing')

    for item in models.Host.objects.all():
        ret = DescribeInstanceMonitorDataRequest.DescribeInstanceMonitorDataRequest()
        ret.set_accept_format('json')
        ret.add_query_param('InstanceId', item.ecsname)
        ret.add_query_param('StartTime', start)
        ret.add_query_param('EndTime', end)
        response = clt.do_action(ret)
        ret_dic=json.loads(response.decode())
        try:
            monitor_data=ret_dic.get('MonitorData').get('InstanceMonitorData')
            ali_jiankong_db(monitor_data, item)
        except AttributeError:
            pass




def ali_jiankong_db(data_list,host_item):
    for item in data_list:
        models.HostMonitor.objects.create(
            host=host_item,
            cpu=int(item.get('CPU')) if item.get('CPU') else None,
            timestamp=item.get('TimeStamp') if item.get('TimeStamp') else None,
            iopswrite=int(item.get('IOPSWrite')) if item.get('IOPSWrite') else None,
            iopsread = int(item.get('IOPSRead')) if item.get('IOPSRead') else None,
            bpsread =int(item.get('BPSRead')) if item.get('BPSRead') else None,
            bpswrite = int(item.get('BPSWrite')) if item.get('BPSWrite') else None,

            intranetbandwidth = int(item.get('IntranetBandwidth')) if item.get('IntranetBandwidth') else None,
            internetbandwidth = int(item.get('InternetBandwidth')) if item.get('InternetBandwidth') else None,

            internetrx = int(item.get('InternetRX')) if item.get('InternetRX') else None,
            internettx = int(item.get('InternetTX')) if item.get('InternetTX') else None,
            intranetrx = int(item.get('IntranetRX')) if item.get('IntranetRX') else None,
            intranettx = int(item.get('IntranetTX')) if item.get('IntranetTX') else None,
        )




#调用请求阿里云api-host接口
@shared_task
def ali_func():
    send_dic = t_ali.api()
    url = settings.HTTP_URL + '/arya/ali_client_api.html/'
    r1 = requests.post(url, json=send_dic)
    #数字27表示 使用机器人， 27是机器人id
    log_indb.delay(27,'/arya/ali_client_api.html/',explain='ali_host_success',msg='ali_host_success')
    return r1.text

#调用请求阿里云api-rds接口
@shared_task
def alirds_func():
    url = settings.HTTP_URL + '/arya/alirds_client_api.html/'
    ret_ali_data = t_ali_rds.ali_rds_fun()
    # ret_ali.send_li 封装在 client端里面
    r1 = requests.post(url, json=ret_ali_data)
    log_indb.delay(27, '/arya/alirds_client_api.html/', explain='ali_rds_success',msg='ali_rds_success')
    return r1.text
