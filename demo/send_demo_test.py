import requests
import json

def encrypt(pwd):
    import hashlib
    '''md5加密，'''
    obj = hashlib.md5()
    obj.update(pwd.encode('utf-8'))
    data = obj.hexdigest()
    return data


#接受数据的url
# url='http://101.201.141.198/api/release/'
url='http://127.0.0.1:8000/api/release/'

#获取token的URL
# url1='http://101.201.141.198/api/auth/'
url1='http://127.0.0.1:8000/api/auth/'

dic={'username':'xuyongming','password':'WqbnZcVp7Lo='}

r1=requests.post(url1,json=dic,headers={ 'Content-Type':'application/json'})

print(r1.text)
if r1.status_code!=200:
    exit('第一步错误')


#获取到token
token=json.loads(r1.text)['token']
key='0SM35tyB%'
name='jenkins'

JG=token+name+key
md5_key=encrypt(JG)

tok={
    'key':md5_key,
     'state':'test',
     'tag':'get',
    'data':{
        'timestamp':32213213,
        'app':'payment2',
        'environment':'测试环境',
        'package': {
        'jar': [],
        'war': ['admin.test.v76831_20180803103634.war', 'osspath','md5'],
        'class': [],
        'properties': [],
        'xml': ['server.xml',],
        'key': []
    },
    }
}
r2=requests.post(url,json=tok,headers={ 'Content-Type':'application/json'})

print(r2.status_code)
print(r2.text)



