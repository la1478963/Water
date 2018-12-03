#!/usr/bin/env python
#coding=utf-8
import requests
import json
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526 import DescribeDisksRequest
from aliyunsdkecs.request.v20140526 import DescribeClassicLinkInstancesRequest

from app01.task import log_indb

class AliRequestApi(object):
    def __init__(self,diyu):
        self.diyu = diyu
        self.clt = client.AcsClient('LTAIH9CwyQbfA0h3',
                       'lY8NnmUIFpfyYFXRs3IHVXhC2Ou6tZ',
                        self.diyu)
    def disk(self,DiskPageSize,DiskPageNumber):
        # 请求磁盘数据
        request = DescribeDisksRequest.DescribeDisksRequest()
        request.set_accept_format('json')
        request.add_query_param('RegionId', self.diyu)
        request.add_query_param('PageSize', DiskPageSize)
        request.add_query_param('PageNumber', DiskPageNumber)
        # 发起请求
        response = self.clt.do_action(request)
        return response.decode()
    def func(self,PageNumber):
        # 请求ecs数据
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format('json')
        # for num in range(2):
        request.add_query_param('RegionId', self.diyu)
        request.add_query_param('PageNumber', PageNumber)
        # 发起请求
        response = self.clt.do_action(request)
        return response.decode()

    def vpc_inter(self,ecsname):
        vpc_inter_request = DescribeClassicLinkInstancesRequest.DescribeClassicLinkInstancesRequest()
        vpc_inter_request.set_accept_format('json')
        vpc_inter_request.add_query_param('RegionId', self.diyu)
        vpc_inter_request.add_query_param('InstanceId', ecsname)

        # 发起请求
        response = self.clt.do_action(vpc_inter_request)

        return response.decode()


    def vpc_combination(self,ret_vpc_inter):
        vpc_li=json.loads(ret_vpc_inter)['Links']['Link']
        try :
            return list(item['VpcId'] for item in vpc_li)
        except KeyError:
            return None


    def ecs_combination(self,ret_ecs):
        send_dic = {}
        PageSize = json.loads(ret_ecs)['PageSize']
        item_host = json.loads(ret_ecs)['Instances']['Instance']
        for i in range(PageSize):
            # ECS不包含磁盘的数据
            try:
                host_dic = {}
                host_dic['ali_id'] = item_host[i]['InstanceId']
                host_dic['disk'] = []
                host_dic['sn'] = item_host[i]['SerialNumber']
                host_dic['mem'] = str(item_host[i]['Memory'] / 1024) + 'G'
                host_dic['cpu'] = item_host[i]['Cpu']
                stop_t = self.func_time(item_host[i]['ExpiredTime'])
                start_t = self.func_time(item_host[i]['StartTime'])
                host_dic['stoptime'] = stop_t
                host_dic['starttime'] = start_t
                host_dic['hostname'] = item_host[i]['InstanceName']
                host_dic['ostype'] = item_host[i]['OSType']
                host_dic['osname'] = item_host[i]['OSName']
                host_dic['status'] = item_host[i]['Status']
                #VPN网络环境
                host_dic['vpc_net'] = item_host[i]['VpcAttributes']['VpcId']
                #所属交换机
                host_dic['vswitch'] = item_host[i]['VpcAttributes']['VSwitchId']
                host_dic['speed'] = str(item_host[i]['InternetMaxBandwidthOut']) + 'M'

                ret_vpc_inter=self.vpc_inter(host_dic['ali_id'])
                #Vpcid 列表， 目前业务 只有一个值
                host_dic['vpc_con']=self.vpc_combination(ret_vpc_inter)
                try:
                    host_dic['eth1'] = item_host[i]['PublicIpAddress']['IpAddress'][0]
                except IndexError:
                    #eth1 没有ip
                    log_indb.delay(27,'/arya/ali_client_api.html/',
                                   explain='ali_host_error:ecs_combination eth1 not have ip')
                try:
                    host_dic['eth0'] = item_host[i]['InnerIpAddress']['IpAddress'][0]
                except IndexError:
                    host_dic['eth0'] = item_host[i]['VpcAttributes']['PrivateIpAddress']['IpAddress'][0]
                if host_dic['ali_id'] in send_dic.keys():
                    log_indb.delay(27, '/arya/ali_client_api.html/',
                           explain='ali_host_error:ecs_combination eth0 not have ip')
                else:
                    send_dic[host_dic['ali_id']] = host_dic
            except IndexError:
                log_indb.delay(27, '/arya/ali_client_api.html/',
                       explain='ali_host_error:ecs_combination main indexError')
                break
        return send_dic

    def disk_combination(self,ret_disk,JG_dic):
        #处理磁盘数据
        item_list=json.loads(ret_disk)['Disks']['Disk']
        item_page_size=json.loads(ret_disk)['PageSize']
        for i in range(item_page_size):
            disk_dic={}
            disk_dic['size']=str(item_list[i]['Size'])+'G'
            disk_dic['route']=item_list[i]['Device']
            host=item_list[i]['InstanceId']
            if host in JG_dic.keys():
                JG_dic[host]['disk'].append(disk_dic)
            else:
                JG_dic[host]={}
                JG_dic[host]['disk'] = []
                JG_dic[host]['disk'].append(disk_dic)
        return JG_dic

    def func_time(self,t):
        if 'T' in t:
            num = t.index('T')
            return t[:num]
        else:
            log_indb.delay(27, '/arya/ali_client_api.html/',
               explain='ali_host_error:func_time T not in t')
            return t

def api():
    #组合数据
    JG_dic={}
    diyu_li=['ap-southeast-1', 'cn-beijing']
    for diyu in diyu_li:
        #拿ECS数据
        A=AliRequestApi(diyu)
        ret_ecs=A.func(11)
        TotalCount=json.loads(ret_ecs)['TotalCount']
        PageNumber=TotalCount//10
        #拿每台
        for i in range(1,PageNumber+2):
            ret_ecs = A.func(i)
            send_dic=A.ecs_combination(ret_ecs)
            JG_dic.update(send_dic)

        #拿磁盘数据
        ret_disk=A.disk(1,1)
        disk_total_count = json.loads(ret_disk)['TotalCount']
        disk_page_size=disk_total_count%10
        disk_page_number=disk_total_count//10

        for i in range(1,disk_page_number+2):
            try:
                ret_disk = A.disk(10, i)
                JG_dic=A.disk_combination(ret_disk,JG_dic)
            except IndexError:
                if disk_page_size != 0:
                    ret_disk=A.disk(disk_page_size,disk_page_number+1)
                    JG_dic=A.disk_combination(ret_disk,JG_dic)

    return JG_dic

if __name__ == '__main__':
    a=api()