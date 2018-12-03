#!/usr/bin/env python
#coding=utf-8
import json
from django.conf import settings
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeInstanceVncUrlRequest
from aliyunsdkcore.profile import region_provider



# ins_id='i-2ze856kmd4rze1p4nr7e'

class WebSSH(object):
    def __init__(self,host_ins_id):
        self.host_ins_id=host_ins_id
        self.pwd = '123456'
        self.url = 'https://g.alicdn.com/aliyun/ecs-console-vnc/0.0.7/index.html?' \
                   'vncUrl={0}&instanceId={1}&isWindows=false&password={2}'
        self.clt=client.AcsClient(settings.ACCESSKEY_ID,
                       settings.ACCESSKEY_KEY,
                       'cn-beijing')


    def run(self):
        # 设置参数
        request = DescribeInstanceVncUrlRequest.DescribeInstanceVncUrlRequest()
        request.set_accept_format('json')
        request.add_query_param('RegionId', 'cn-beijing')
        request.add_query_param('InstanceId', self.host_ins_id)
        # 发起请求
        response = self.clt.do_action(request)
        ret=response.decode('utf-8')
        ret_dic=json.loads(ret)
        print(ret_dic.get('RequestId'))
        JG=self.url.format(ret_dic.get('VncUrl'),self.host_ins_id,self.pwd)
        return JG