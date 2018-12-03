import hashlib
import base64
from django.forms.boundfield import BoundField
# print('sdgfuaejkdlshuifladsilfjkdasfd'.rstrip('ewrwerewfdsfsrewrerw'))
# s1 = base64.encodestring('hello'.encode())
# s2 = base64.decodestring(s1)
# print(s1.decode(),'---', s2.decode())
class jiami(object):
    @staticmethod
    def encrypt(pwd):
        '''md5加密，用户CMDB登录密码'''
        obj=hashlib.md5()
        obj.update(pwd.encode('utf-8'))
        data=obj.hexdigest()
        return data

    def base_str_encrypt(self,s1):
        '''base64加密'''
        s1=str(s1)+'we!458@EWQ'
        return base64.encodestring(s1.encode()).decode()

    def base_str_decrypt(self,s2):
        '''base64解密'''
        try:
            s2=base64.decodestring(str(s2).encode())

            return s2.decode()[:-10]
        # return s2.decode().rstrip('we!458@EWQ')
        except Exception:
            return '不识别'



# A=jiami()
# B=A.base_str_encrypt('hello')
# print(B)
# print(A.base_str_decrypt(B))
