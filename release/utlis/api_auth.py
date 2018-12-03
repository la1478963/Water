from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rbac import models
from utlis.jiami_class import jiami

class TokenAuthtication(BaseAuthentication):
    def authenticate(self, request):
        ret_dic = {'status': True, 'tag': 'send', 'error': None, 'state': None}
        """
        :param request:
        :return:
            （user，auth） 表示认证成功，并将元组分别复制给request.user/request.auth
             raise AuthenticationFailed('认证失败') 表示认证失败
             None, 表示匿名用户
        """
        token = request.data.get('key')
        if not token:
            ret_dic['status']=False
            raise AuthenticationFailed('用户Key未携带')
        token_li = models.User.objects.filter(token__isnull=False)
        key = '0SM35tyB%'
        name = ['jenkins', 'ansible']
        for tok_obj in token_li:
            JG_str=tok_obj.token+name[0]+key
            JG=jiami().encrypt(JG_str)
            if token == JG:
                return (tok_obj.username,tok_obj)

        raise AuthenticationFailed('token已失效或错误')
