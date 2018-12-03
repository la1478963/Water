#!/usr/bin/env python3
# -*- coding: utf8 -*-
from flask import Flask,request
from ansible_api import MyApi
import json


app = Flask(__name__)


ans_run_dic={
    'shell':'run',
    'playbook':'run_playbook'
}


@app.route('/run',methods=['GET','POST'])
def run_ansible():
    ret={'status':False,'data':'','error':'','msg':''}
    if request.method=='POST':
        res_data=request.get_data()
        if res_data:
            data_dic=json.loads(res_data.decode('utf-8'))
        else:
            data_dic=request.form
        '''
        dic={
            msg:'shell or playbook'
            host:'webserver or all',
            module:'command',
            args:'ls',
        }
        '''
        msg=data_dic.get('msg')
        host=data_dic.get('host')
        module=data_dic.get('module')
        args=data_dic.get('args')
        if not host and not module:
            ret['error']='host and module is  not None'
            return json.dumps(ret)
        if not msg:
            ret['error']='msg is not Noe'
            return json.dumps(ret)

        # host='webserver'
        api = MyApi(host)
        # api = MyApi(<hostfile>)


        if msg in ans_run_dic.keys():
            func=getattr(api,ans_run_dic[msg])
            # 执行 Ad-hoc
            # api.run(host, 'command', 'ls /')
            func(host, module, args)
            ret['data'] = api.get_result()
            ret['status'] = True
        else:
            ret['error']='ansible not have  function'

        return json.dumps(ret)




if __name__ == '__main__':
    # app.run(host='127.0.0.1')
    app.run()



