import requests
import json
import datetime


def encrypt(pwd):
    import hashlib
    '''md5加密，'''
    obj = hashlib.md5()
    obj.update(pwd.encode('utf-8'))
    data = obj.hexdigest()
    return data

#ip port 需要修改

#获取token的URL
url1='http://101.201.141.198/api/auth/'
# url1='http://127.0.0.1:8000/api/auth/'

#接受数据的url
url='http://101.201.141.198/api/release/'
# url='http://127.0.0.1:8000/api/release/'

nowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

dic={'username':'xuyongming','password':'WqbnZcVp7Lo='}

r1=requests.post(url1,json=dic,headers={ 'Content-Type':'application/json'})

if r1.status_code!=200:
    print(r1.text)
    exit('第一步错误')


#获取到token
token=json.loads(r1.text)['token']
key='0SM35tyB%'
name='jenkins'

JG=token+name+key
md5_key=encrypt(JG)
print(md5_key)
tok={
    'key':md5_key,
     'state':'pack',
     'tag':'send',
    'data':{
        'timestamp':nowTime,
        'app':'payment2',
        'environment':None,
        'package': {
            'jar': [],
            'war': ['pp1pp.war', 'osspath','md5'],
            'class': [],
            'properties': [],
            'xml': [],
            'key': []
        },
    }
}
r2=requests.post(url,json=tok,headers={ 'Content-Type':'application/json'})


print(r2.text)
JG=json.loads(r2.text)
if JG['status']:
    print('------------成功')


