#!/usr/bin/env python
#coding=utf-8

import json
from utlis.time_class import Time
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeInstanceMonitorDataRequest
from aliyunsdkcore.profile import region_provider


start,end=Time().ali_def_monitor()
# print(start,end)
in_id='i-2ze856kmd4rze1p4nr7e'


#region_provider.modify_point('ecs', '<regionId>', 'ecs.<regionId>.aliyuncs.com')

clt = client.AcsClient('LTAIH9CwyQbfA0h3',
                       'lY8NnmUIFpfyYFXRs3IHVXhC2Ou6tZ',
                       'cn-beijing')

# 设置参数
request = DescribeInstanceMonitorDataRequest.DescribeInstanceMonitorDataRequest()
request.set_accept_format('json')

request.add_query_param('InstanceId', in_id)
request.add_query_param('StartTime', start)
request.add_query_param('EndTime', end)

# 发起请求
response = clt.do_action(request)

print (json.loads(response.decode()))

'''
from utlis.time_class import Time

JG=Time().ali_monitor()

print(JG)
'''




















