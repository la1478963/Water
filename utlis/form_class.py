from django.forms import Form
from django.forms import fields
from django.forms import widgets
from rbac import models
from django.core.exceptions import ValidationError
class LoginForm(Form):
    username=fields.CharField(
        max_length=15,
        min_length=2,
        required=True,
        error_messages={'required':'用户名不能为空','invalid':'输入不合规'},
        # widget = widgets.TextInput(attrs={'class': 'form-control loon luser'})
        widget = widgets.TextInput(attrs={'class': 'form-control loon luser','value':'用户名'})
    )
    password = fields.CharField(
        required=True,
        max_length=32,
        min_length=2,
        error_messages={'required': '密码不能为空', 'invalid': '输入不合规'},
        widget=widgets.PasswordInput(attrs={'class': 'form-control loon lpass', 'value': '密码'})
    )

class RegisterForm(Form):
    username=fields.CharField(
        max_length=12,
        min_length=2,
        required=True,
        error_messages={'required':'用户名不能为空','invalid':'输入不合规'},
        widget = widgets.TextInput(attrs={'class': 'form-control loon luser','value':'用户名'})
    )
    password = fields.CharField(
        required=True,
        max_length=32,
        min_length=4,
        error_messages={'required': '密码不能为空', 'invalid': '输入不合规'},
        widget=widgets.TextInput(attrs={'class': 'form-control loon lpass', 'value': '密码'})
    )
    password_confum = fields.CharField(
        required=True,
        max_length=32,
        min_length=4,
        error_messages={'required': '密码不能为空', 'invalid': '输入不合规'},
        widget=widgets.TextInput(attrs={'class': 'form-control loon lpass', 'value': '确认密码'})
    )
    def clean(self):
        try:
            if self.cleaned_data['password'] == self.cleaned_data['password_confum']:
                return self.cleaned_data
            else:
                self.add_error('password_confum',ValidationError('密码不一致'))
                return self.cleaned_data
        except KeyError:
            pass

'''hostname= models.CharField(max_length=32, blank=True, null=True, verbose_name='阿里云主机名')
    ecsname= models.CharField(max_length=32, blank=True, null=True, verbose_name='阿里云实例ID')
    logining=models.ManyToManyField(to='Login',blank=True, null=True, verbose_name='授权用户')
    login_port = models.CharField(max_length=16, default='22',blank=True, null=True, verbose_name='ssh登录端口')
    cpu= models.ForeignKey(to='Cpu',blank=True, null=True, verbose_name='CPU')
    motherboard= models.ForeignKey(to='Motherboard',blank=True, null=True, verbose_name='主板')
    mem= models.ForeignKey(to='Memory',blank=True, null=True, verbose_name='内存/M')
    speed = models.IntegerField(blank=True, default='2',null=True, verbose_name='带宽/M')
    disks= models.ManyToManyField(to='Disk', blank=True, null=True, verbose_name='磁盘')
    eth1_network= models.CharField(max_length=32, blank=True, null=True, verbose_name='公网IP')
    eth0_network= models.CharField(max_length=32, blank=True, null=True, verbose_name='私网IP')
    uuid= models.CharField(max_length=64, blank=True, null=True, verbose_name='uuid')
    os= models.ForeignKey(to='Os', blank=True, null=True, verbose_name='操作系统') #os+版本号
    kernel= models.CharField(max_length=32, blank=True, null=True, verbose_name='系统内核') #内核+版本号
    the_upper=models.ForeignKey(to='Host',blank=True,null=True,verbose_name='宿主机',related_name='upper')
    source=models.ForeignKey(to='Source',blank=True,null=True,verbose_name='来源类型')
    osarch_choices=((1,'64位'),(2,'32位'))
    ossarch=models.SmallIntegerField(verbose_name='操作系统位数', choices=osarch_choices,blank=True,null=True,)
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    state_choices=(
        (1,'上线'),
        (2,'下线'),
        (3,'关机'),
        (4,'删除'),
    )
    state = models.SmallIntegerField(verbose_name='主机状态', choices=state_choices,blank=True,null=True,)'''
# class HostForm(Form):
#     id = fields.IntegerField()
#     hostname=fields.CharField(error_messages={'required': '不能为空'},
#         widget=widgets.TextInput(attrs={'class': 'form-control','name':'hostname'}))
#




class NewForm(Form):
    id=fields.IntegerField()
    url=fields.URLField(
        # required==True,
        error_messages={'required': '不能为空'},
        widget=widgets.TextInput(attrs={'class': 'form-control','id':'Url'})
    )
    title=fields.CharField(
        required=True,
        error_messages={'required':'不能为空'},
        widget=widgets.TextInput(attrs={'class': 'form-controls','id':'title'})
    )
    summary=fields.CharField(
        required=True,
        max_length=2048,
        error_messages={'required': '不能为空','invalid':'输入不合规'},
        widget=widgets.TextInput(attrs={'class': 'form-control','id':'summary'})
    )

    like_count=fields.IntegerField(
        required=True,
        error_messages={'required': '不能为空','invalid':'输入不合规'},
        widget=widgets.TextInput(attrs={'class': 'form-control'})
    )

    img=fields.CharField(
        required=True,
        error_messages={'required': '不能为空', 'invalid': '输入不合规'},
        widget=widgets.TextInput(attrs={'class': 'form-control'})
    )

    news_id=fields.ChoiceField(
        choices=[],
        widget=widgets.Select(attrs={'class': 'form-control'})
    )
    user_id=fields.ChoiceField(
        choices=[],
        widget=widgets.Select(attrs={'class': 'form-control'})
    )
    def __init__(self,*args,**kwargs):
        super(NewForm,self).__init__(*args,**kwargs)
        self.fields['news_id'].choices=models.NewsType.objects.values_list('id','name')
        self.fields['user_id'].choices=models.LoginUser.objects.values_list('id','username')


