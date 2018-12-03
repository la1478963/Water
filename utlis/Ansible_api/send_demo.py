


import requests
import json
ansible_api='http://ip:port/run'  #这里记得把ip  port 改掉

dic={
        'msg':'shell',
        'host':'webserver',
        'module':'command',
        'args':'ls /',
    }
r1=requests.post(ansible_api,json=dic)

ret_dic=json.loads(r1.text)
if ret_dic['status']:
    data=ret_dic['data']
    for k,v in data.items():
        print(k,v)




