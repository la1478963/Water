import requests
import json



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



dic={'username':'xuyongming','password':'WqbnZcVp7Lo='}

r1=requests.post(url1,json=dic,headers={ 'Content-Type':'application/json'})

if r1.status_code!=200:
    exit('第一步错误')


#获取到token
token=json.loads(r1.text)['token']
key='0SM35tyB%'
name='jenkins'

JG=token+name+key
md5_key=encrypt(JG)
print('加密的key----',md5_key)


environment_list = (
        ('develop','开发环境'),
        ('test','测试环境'),
        ('gray','灰度环境'),
        ('pressure','压力环境'),
        ('production','生产环境'),
    )

tok={
    'key':md5_key,
     'state':'pack',
     'tag':'get',
    'data':{
        'timestamp':123412321,
        'app':'admin',
        'environment':'test',
        'package': {
            'jar': [],
            'war': ['admin.test.v75970_20180625203211.war', '',''],
            'class': [],
            'properties': [],
            'xml': [],
            'key': []
        },
    }
}
r2=requests.get(url,json=tok,headers={ 'Content-Type':'application/json'})


print('所有返回值',r2.text)
JG=json.loads(r2.text)
if JG['status']:
    print('------------成功')
else:
    print('===失败',JG['error'])


