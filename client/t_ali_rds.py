#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
import json
from aliyunsdkecs.request.v20140526 import DescribeDisksRequest
import requests
from aliyunsdkcore import client
from aliyunsdkrds.request.v20140815 import DescribeDBInstanceAttributeRequest
from aliyunsdkrds.request.v20140815 import DescribeDBInstancesRequest
from aliyunsdkrds.request.v20140815 import DescribeResourceUsageRequest
from aliyunsdkrds.request.v20140815 import DescribeDatabasesRequest
from utlis.log_class import Logger
import threading
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    from threading import get_ident

class AliRDS(object):
    def __init__(self,diyu):
        self.send_li=[]
        self.diyu=diyu
        self.logger = Logger(loglevel=1, logger="fox").getlog()
        self.clt = client.AcsClient('LTAIH9CwyQbfA0h3',
                       'lY8NnmUIFpfyYFXRs3IHVXhC2Ou6tZ',
                       self.diyu)
    def get_list(self):
        # 设置参数
        request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
        request.set_accept_format('json')
        request.add_query_param('RegionId', self.diyu)
        # 发起请求
        response = self.clt.do_action(request)
        return response.decode()

    def func_list(self,li):
        #组合数据
        li=json.loads(li)['Items']['DBInstance']
        for i in li:
            case_dic = {}
            case_dic[i['DBInstanceId']]={
                'hostname':i['DBInstanceDescription'],
                'caseid':i['DBInstanceId'],
            }
            self.send_li.append(case_dic)

    def case(self):
        #请求实例信息
        for content in self.send_li:
            for case_id in content.keys():
                #拿RDS实例
                request = DescribeDBInstanceAttributeRequest.DescribeDBInstanceAttributeRequest()
                request.set_accept_format('json')
                request.add_query_param('DBInstanceId', case_id)
                # 发起请求
                response = self.clt.do_action(request)

                #拿磁盘使用
                disk_use_request = DescribeResourceUsageRequest.DescribeResourceUsageRequest()
                disk_use_request.set_accept_format('json')
                disk_use_request.add_query_param('DBInstanceId', case_id)
                # 发起请求
                disk_use_response = self.clt.do_action(disk_use_request)

                #拿实例下的库,以及用户
                db_request = DescribeDatabasesRequest.DescribeDatabasesRequest()
                db_request.set_accept_format('json')
                db_request.add_query_param('DBInstanceId', case_id)
                # 发起请求
                self.logger.info(case_id)
                db_response = self.clt.do_action(db_request)

                #每个实例
                t=threading.Thread(target=self.func_case,args=(response.decode(),
                    content,case_id,disk_use_response.decode(),
                    db_response.decode()))
                t.start()

    def func_case(self,case_item,content,case_id,disk_use_item,db_item):
                #self, 实例对象,每个组合后的数据,#实例id,使用磁盘对象,库对象（包括用户）
        # 组合数据
        item=json.loads(case_item)['Items']['DBInstanceAttribute'][0]
        try:
            use_disk=json.loads(disk_use_item)['DiskUsed']
        except KeyError:
            self.logger.error('组合数据,请求阿里云返回结果异常,上面caseid,下面RequestID->')
            self.logger.error(json.loads(disk_use_item))
            use_disk=0
        database_list=json.loads(db_item)['Databases']['Database']
        url=item['ConnectionString']
        cpu=item['DBInstanceCPU']
        maxcon=item['MaxConnections']
        mem=item['DBInstanceMemory']
        iops=item['MaxIOPS']
        disk=item['DBInstanceStorage']
        types=item['Engine']+item['EngineVersion']
        master=item.get('IncrementSourceDBInstanceId','')
        content[case_id]['url']=url
        content[case_id]['cpu']=cpu
        content[case_id]['maxcon']=maxcon
        content[case_id]['mem']=mem
        content[case_id]['iops']=iops
        content[case_id]['disk']=disk
        content[case_id]['use_disk']=round(use_disk/1024/1024/1024,2)
        content[case_id]['type']=types
        content[case_id]['master']=master
        db_list=[]
        for database_item in database_list:
            db_dic = {}
            user_all_list = []
            user_dic = {}
            DBName=database_item['DBName']
            for user in database_item['Accounts']['AccountPrivilegeInfo']:
                user_list=[]
                user_list.insert(0,user['Account'])
                user_list.insert(1,user['AccountPrivilege'])
                user_all_list.append(user_list)
            user_dic['user']=user_all_list
            # user_dic['dbname']=DBName
            db_dic[DBName]=user_dic
            db_list.append(db_dic)
        content[case_id]['db'] = db_list


def ali_rds_fun():
    ret_li=[]
    diyu_li=['ap-southeast-1','cn-beijing']
    for diyu in diyu_li:
        ret_ali = AliRDS(diyu)
        case_list = ret_ali.get_list()
        ret_ali.func_list(case_list)
        ret_ali.case()
        ret_li+=ret_ali.send_li
    return ret_li




if __name__ == '__main__':
    ali=AliRDS()
    case_list=ali.get_list()
    ali.func_list(case_list)
    ali.case()
    print(ali.send_li)




