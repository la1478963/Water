#!/usr/bin/env python
#coding=utf-8
import json
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeInstanceVncUrlRequest
from aliyunsdkcore.profile import region_provider
#region_provider.modify_point('ecs', '<regionId>', 'ecs.<regionId>.aliyuncs.com')
ins_id='i-2ze856kmd4rze1p4nr7e'
clt = client.AcsClient('LTAIH9CwyQbfA0h3',
                       'lY8NnmUIFpfyYFXRs3IHVXhC2Ou6tZ',
                       'cn-beijing')

# 设置参数
request = DescribeInstanceVncUrlRequest.DescribeInstanceVncUrlRequest()
request.set_accept_format('json')

request.add_query_param('RegionId', 'cn-beijing')
request.add_query_param('InstanceId', ins_id)

# 发起请求
response = clt.do_action(request)

ret=response.decode('utf-8')
ret_dic=json.loads(ret)
print(ret_dic.get('RequestId'))

pwd='123456'




url='https://g.alicdn.com/aliyun/ecs-console-vnc/0.0.7/index.html?vncUrl={0}&instanceId={1}&isWindows=false&password={2}'



JG=url.format(ret_dic.get('VncUrl'),ins_id,pwd)


print(JG)