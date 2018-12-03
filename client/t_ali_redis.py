#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
client = AcsClient('LTAIH9CwyQbfA0h3',
                   'lY8NnmUIFpfyYFXRs3IHVXhC2Ou6tZ'
                   ,'cn-beijing')

request = CommonRequest()
request.set_accept_format('json')
request.set_domain('r-kvstore.aliyuncs.com')
request.set_method('POST')
request.set_version('2015-01-01')
request.set_action_name('DescribeInstances')



response = client.do_action_with_exception(request)
print (response.decode())