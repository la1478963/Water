from django.db import models
environment_choices = (
        (1, '开发环境'),
        (2, '测试环境'),
        (3, '灰度环境'),
        (4, '压测环境'),
        (5, '生产环境'),
    )




########权限相关
class Menu(models.Model):
    """菜单组"""
    name = models.CharField(max_length=32,verbose_name='菜单', blank=True, null=True)
    is_menu=models.ForeignKey(to='Menu',null=True,blank=True,verbose_name='母菜单')
    class Meta:
        verbose_name_plural = "菜单表"
    def __str__(self):
        return self.name

class Group(models.Model):
    """权限组"""
    name = models.CharField(verbose_name='组名称',max_length=16, blank=True, null=True)
    menu = models.ForeignKey(verbose_name='所属菜单',to='Menu', blank=True,null=True)
    class Meta:
        verbose_name_plural = "权限组"
    def __str__(self):
        return self.name

class Permission(models.Model):
    """权限表URL"""
    name = models.CharField(verbose_name='标题', max_length=32)
    url = models.CharField(verbose_name="含正则URL", max_length=64)
    menu_gp = models.ForeignKey(verbose_name='默认选中的组内权限ID', to='Permission', null=True, blank=True, related_name='x1')
    code = models.CharField(verbose_name="代码", max_length=16)
    group = models.ForeignKey(verbose_name='所属组', to="Group")
    class Meta:
        verbose_name_plural = "权限URL表"
    def __str__(self):
        return self.name


class PteamPermission(models.Model):
    """项目组权限表"""
    name = models.CharField(max_length=32, blank=True,null=True,verbose_name='项目读写')
    permissions = models.ManyToManyField(verbose_name='具有的所有权限', to='Permission', blank=True,null=True)
    class Meta:
        verbose_name_plural = "项目权限表"
    def __str__(self):
        return self.name


class User(models.Model):
    """用户表"""
    name = models.CharField(max_length=32, verbose_name='真实名称', blank=True, null=True)
    username=models.CharField(max_length=16, blank=True, null=True, verbose_name='用户名')
    password=models.CharField(max_length=32, blank=True, null=True, verbose_name='密码')
    token=models.CharField(max_length=64, blank=True, null=True, verbose_name='token')
    pteamper = models.ForeignKey(verbose_name='项目权限表', to="PteamPermission", blank=True,null=True,related_name='user')
    pteams =  models.ManyToManyField(verbose_name='项目组', to="Pteam", blank=True,null=True,related_name='user')
    # pteam =  models.ForeignKey(verbose_name='项目组', to="Pteam", blank=True,null=True,related_name='user')
    class Meta:
        verbose_name_plural = "用户表"
    def __str__(self):
        return self.name

class Pteam(models.Model):
    name=models.CharField(max_length=16, verbose_name='项目组名', blank=True, null=True)
    groupname=models.CharField(max_length=16, verbose_name='项目组', blank=True, null=True)
    class Meta:
        verbose_name_plural = "项目组"
    def __str__(self):
        return self.groupname



############################host 相关

class Memory(models.Model):
    '''内存'''
    size=models.CharField(max_length=32, blank=True, null=True, verbose_name='内存/G')
    width=models.CharField(max_length=8, blank=True, null=True, verbose_name='位数')
    locator=models.CharField(max_length=16, blank=True, null=True, verbose_name='插槽')
    type=models.CharField(max_length=16, blank=True, null=True, verbose_name='内存类型')
    def __str__(self):
        return self.size
    class Meta:
        verbose_name_plural = "内存表"

class Disk(models.Model):
    '''磁盘'''
    path = models.CharField(max_length=64, blank=True, null=True, verbose_name='挂载路径')
    size = models.CharField(max_length=16, blank=True, null=True, verbose_name='磁盘大小/G')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    def __str__(self):
        return self.size
    class Meta:
        verbose_name_plural = "磁盘表"

class Os(models.Model):
    '''系统'''
    name=models.CharField(max_length=16, blank=True, null=True, verbose_name='系统名称')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "操作系统表"


class Login(models.Model):
    '''登录相关'''
    login_name = models.CharField(max_length=16, default='root', verbose_name='登录用户名')
    login_pwd= models.CharField(max_length=64, blank=True, null=True, verbose_name='登录密码')
    auth=models.CharField(max_length=8,blank=True, null=True, verbose_name='具有权限')
    def __str__(self):
        return self.login_name
    class Meta:
        verbose_name_plural = "主机用户表"

class Lable(models.Model):
    #标签
    name = models.CharField(max_length=16, blank=True, null=True, verbose_name='标签')
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "标签"

class VpcNet(models.Model):
    title=models.CharField(max_length=32, blank=True, null=True, verbose_name='VPC网络ID')
    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = "VPC网络ID"

class VpcSwitch(models.Model):
    title=models.CharField(max_length=32, blank=True, null=True, verbose_name='VPC交换机ID')
    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = "VPC交换机"


class Host(models.Model):
    '''主机,阿里云eth0 内网网卡， eth1 公网网卡'''
    hostname= models.CharField(max_length=64, blank=True, null=True, verbose_name='阿里云主机名')
    ecsname= models.CharField(max_length=64, blank=True, null=True, verbose_name='阿里云实例ID')
    logining=models.ManyToManyField(to='Login',blank=True, null=True, verbose_name='授权用户')
    login_port = models.CharField(max_length=16, default='22',blank=True, null=True, verbose_name='ssh登录端口')
    cpu= models.CharField(max_length=8,blank=True, null=True, verbose_name='CPU')
    lab= models.ForeignKey(to='Lable',blank=True, null=True, verbose_name='标签')
    mem= models.CharField(max_length=8,blank=True, null=True, verbose_name='内存/M')
    # mem= models.ForeignKey(to='Memory',blank=True, null=True, verbose_name='内存/M')
    speed = models.CharField(max_length=8,blank=True, default='5',null=True, verbose_name='带宽/M')
    disks= models.ManyToManyField(to='Disk', blank=True, null=True, verbose_name='磁盘')
    eth1_network= models.CharField(max_length=32, blank=True, null=True, verbose_name='公网IP')
    eth0_network= models.CharField(max_length=32,verbose_name='私网IP')
    sn= models.CharField(max_length=64, blank=True, null=True, verbose_name='sn')
    os= models.ForeignKey(to='Os', blank=True, null=True, verbose_name='操作系统') #os+版本号
    kernel= models.CharField(max_length=64, blank=True, null=True, verbose_name='系统内核') #内核+版本号
    the_upper=models.ForeignKey(to='Host',blank=True,null=True,verbose_name='宿主机',related_name='upper')
    source=models.ForeignKey(to='Source',blank=True,null=True,verbose_name='来源类型')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    createtime = models.CharField(max_length=32, blank=True, null=True, verbose_name='创建时间')
    expirytime = models.CharField(max_length=32, blank=True, null=True, verbose_name='到期时间')
    vpcnet = models.ForeignKey(to='VpcNet', blank=True, null=True, verbose_name='VPC网络',related_name='vpcnet')
    vpcsw = models.ForeignKey(to='VpcSwitch', blank=True, null=True, verbose_name='VPC交换机')
    vpccon = models.ForeignKey(to='VpcNet', blank=True, null=True, verbose_name='VPC连接',related_name='vpccon')
    state_choices=(
        (1,'Running'),
        (2,'下线'),
        (3,'关机'),
        (4,'删除'),
    )
    state = models.SmallIntegerField(verbose_name='主机状态', choices=state_choices,blank=True,null=True,)
    def __str__(self):
        return self.eth0_network
    class Meta:
        verbose_name_plural = "主机表"


class Source(models.Model):
    '''来源：阿里云、物理机（某机房等）'''
    name=models.CharField(max_length=16,blank=True,null=True,verbose_name='来源')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "主机来源表"


class HostMonitor(models.Model):
    '''主机使用率数据(监控)'''
    timestamp=models.CharField(max_length=64,blank=True,null=True,verbose_name='UTC时间')
    host=models.ForeignKey(to='Host',blank=True,null=True,verbose_name='实例id',related_name='hm')
    cpu=models.IntegerField(blank=True,null=True,verbose_name='cpu使用率')
    mem=models.IntegerField(blank=True,null=True,verbose_name='内存使用率')
    load=models.IntegerField(blank=True,null=True,verbose_name='系统负载')

    iopswrite=models.IntegerField(blank=True,null=True,verbose_name='系统盘IO写次数/s')
    iopsread=models.IntegerField(blank=True,null=True,verbose_name='系统盘IO读次数/s')
    bpsread=models.IntegerField(blank=True,null=True,verbose_name='系统盘IO读带宽Byte/s')
    bpswrite=models.IntegerField(blank=True,null=True,verbose_name='系统盘IO写带宽Byte/s')

    intranetbandwidth=models.IntegerField(blank=True,null=True,verbose_name='内网带宽kbits/s')
    internetbandwidth=models.IntegerField(blank=True,null=True,verbose_name='公网带宽kbits/s')

    internetrx=models.IntegerField(blank=True,null=True,verbose_name='接收的公网流量 kbits')
    internettx=models.IntegerField(blank=True,null=True,verbose_name='发送的公网流量 kbits')
    intranetrx=models.IntegerField(blank=True,null=True,verbose_name='接受的内网流量 kbits')
    intranettx=models.IntegerField(blank=True,null=True,verbose_name='发送的内网流量 kbits')

    def __str__(self):
        return self.timestamp
    class Meta:
        verbose_name_plural = '主机监控数据'

##########业务表

class App(models.Model):
    name=models.CharField(max_length=64,blank=True,null=True,verbose_name='应用名')
    path=models.CharField(max_length=256,blank=True,null=True,verbose_name='应用路径')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    ab_choices = ((1, 'A'), (2, 'B'),(3, 'VPC'))
    ab = models.SmallIntegerField(blank=True, null=True,verbose_name='A/B组', choices=ab_choices)
    environment_choices = (
        (1, '开发环境'),
        (2, '测试环境'),
        (3, '灰度环境'),
        (4, '压测环境'),
        (5, '生产环境'),
    )
    environment =models.SmallIntegerField(blank=True, null=True,verbose_name='环境',choices=environment_choices)
    pteamrole = models.ForeignKey(to='Pteam', blank=True, null=True, verbose_name='项目组', related_name='appteam')
    hosts = models.ManyToManyField(to='Host', blank=True, null=True, verbose_name='对应主机', related_name='apphost')
    class Meta:
        verbose_name_plural = "项目组应用"
        unique_together=[
            ('name','ab','environment'),
        ]
    def __str__(self):
        return self.name
    @property
    def ab_tag(self):
        return self.get_ab_display()
    @property
    def environment_tag(self):
        return self.get_environment_display()

class JiraVersion(models.Model):
    time = models.CharField(max_length=64, blank=True, null=True, verbose_name='流程号')
    version = models.CharField(max_length=32, blank=True, null=True, verbose_name='版本号')
    jira=models.ForeignKey(to='Jira',blank=True, null=True, verbose_name='jira', related_name='jiraver')
    def __str__(self):
        return self.time
    class Meta:
        verbose_name_plural = "版本"

class Jira(models.Model):
    name=models.CharField(max_length=32,blank=True,null=True,verbose_name='Jira需求编号')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "jira_id"

class Project(models.Model):
    name=models.CharField(max_length=32,blank=True,null=True,verbose_name='项目名')
    tag_choices=((1,'刚录入'),(2,'提测'),(3,'已完结'))
    #标识，如果 本次应用上线完成后， 标识变为True
    tag=models.SmallIntegerField(verbose_name='进度',default=1,choices=tag_choices)
    jira=models.ForeignKey(to='Jira', blank=True, null=True, verbose_name='jira', related_name='jr')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "项目"

class Package(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name='包名')
    bool = models.BooleanField(default=0, verbose_name='是否应用')
    disname=models.CharField(max_length=64, blank=True, null=True, verbose_name='原包名')
    osspath = models.CharField(max_length=128, blank=True, null=True, verbose_name='oss路径')
    serverpath = models.CharField(max_length=128, blank=True, null=True, verbose_name='服务器路径')
    packagetype_choices = (
        (1, 'war'),
        (2, 'jar'),
        (3, 'sql'),
        (4, 'xml'),
        (5, 'class'),
        (6, 'properties'),
        (7, 'key'),
        (8, 'other'),
    )
    type=models.SmallIntegerField(blank=True, null=True,verbose_name='类型',choices=packagetype_choices)
    ctime=models.CharField(max_length=32, blank=True, null=True, verbose_name='创建时间')
    md5=models.CharField(max_length=64, blank=True, null=True, verbose_name='md5')
    packenv=models.CharField(max_length=16,blank=True, null=True, default='所有环境', verbose_name='配置所属环境')
    proj=models.ForeignKey(to='Project',blank=True, null=True, verbose_name='所属项目',related_name='pj')
    def __str__(self):
        return self.disname
    class Meta:
        verbose_name_plural = "包"

class Record(models.Model):
    timestamp = models.CharField(max_length=64, blank=True, null=True, verbose_name='时间')
    status = models.CharField(max_length=64, blank=True, null=True, verbose_name='状态')
    project=models.ForeignKey(to='Project', blank=True, null=True, verbose_name='项目', related_name='proj')
    package=models.ManyToManyField(to='Package',blank=True, null=True, verbose_name='包', related_name='pack')
    env=models.ForeignKey(to='RecordEnv',blank=True, null=True, verbose_name='环境', related_name='env')
    def __str__(self):
        return self.timestamp
    class Meta:
        verbose_name_plural = "部署记录"

class RecordEnv(models.Model):
    name=models.CharField(max_length=64, blank=True, null=True, verbose_name='环境')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "部署环境"

'''
class Task(models.Model):
    jira=models.CharField(max_length=32,blank=True,null=True,verbose_name='jira_id')
    projectname=models.CharField(max_length=32,blank=True,null=True,verbose_name='项目')

    def __str__(self):
        return self.jira
    class Meta:
        verbose_name_plural = "发布流程"

class TaskFile(models.Model):
    name=models.CharField(max_length=64,blank=True,null=True,verbose_name='文件名')
    disname=models.CharField(max_length=64,blank=True,null=True,verbose_name='显示文件名')
    osspath=models.CharField(max_length=128,blank=True,null=True,verbose_name='oss路径')
    timestamp=models.CharField(max_length=64,blank=True,null=True,verbose_name='时间')
    environment =models.SmallIntegerField(blank=True, null=True,verbose_name='环境',choices=environment_choices)
    packagetype = models.SmallIntegerField(blank=True, null=True, verbose_name='包类型', choices=packagetype_choices)
    task=models.ForeignKey(to='Task', blank=True, null=True, verbose_name='项目', related_name='ta')

    packagestate = models.ManyToManyField(to='FileState', blank=True, null=True, verbose_name='包状态', related_name='sta')

    def __str__(self):
        return self.disname
    class Meta:
        verbose_name_plural = "包详情"

class FileState(models.Model):
    title=models.CharField(max_length=16,blank=True,null=True,verbose_name='状态')
    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = "包状态"
'''


#############系统操作日志记录表
class OperationLog(models.Model):
    user = models.ForeignKey(to='User', blank=True, null=True, verbose_name='操作员', related_name='us')
    ctime = models.DateTimeField(auto_now_add = True, verbose_name='访问时间')
    url = models.CharField(max_length=256, blank=True, null=True, verbose_name='访问url')
    proj = models.CharField(max_length=32, blank=True, null=True, verbose_name='project')
    action = models.CharField(max_length=32, blank=True, null=True, verbose_name='动作')
    explain = models.CharField(max_length=128, blank=True, null=True, verbose_name='说明')




##########中间件
#阿里云账号
class ALiCloud(models.Model):
    username = models.CharField(max_length=32, blank=True, null=True, verbose_name='登录用户')
    password = models.CharField(max_length=128, blank=True, null=True, verbose_name='登录密码')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    accesskey_id = models.CharField(max_length=128, blank=True, null=True, verbose_name='AccessKey')
    accesskeysecret = models.CharField(max_length=128, blank=True, null=True, verbose_name='AccessKeySecret')
    class Meta:
        verbose_name_plural = "阿里云"
    def __str__(self):
        return self.username

#zk
class Zookeeper(models.Model):
    ip=models.ForeignKey(to='Host',blank=True, null=True, verbose_name='主机ip',related_name='ip_zk')
    port=models.CharField(verbose_name='端口号',blank=True, null=True,default='2181',max_length=8)
    start_user=models.CharField(max_length=16,blank=True,null=True,verbose_name='启动用户',default='appuser')
    zk_tag = models.CharField(max_length=64, blank=True, null=True, verbose_name='标识')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    apps=models.ManyToManyField(to='App', blank=True, null=True, verbose_name='使用应用',related_name='zk')
    class Meta:
        verbose_name_plural = "Zookeeper"
    def __str__(self):
        return self.ip.eth0_network+':'+self.port
        # return self.zk_tag

#kafka
class Kafka(models.Model):
    ip=models.ForeignKey(to='Host',blank=True, null=True, verbose_name='主机ip',related_name='ip_kafka')
    port=models.CharField(verbose_name='端口号',blank=True, null=True,max_length=8,default='9092')
    start_user=models.CharField(max_length=16,blank=True,null=True,verbose_name='启动用户',default='appuser')
    kafka_tag = models.CharField(max_length=64, blank=True, null=True, verbose_name='标识')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    apps=models.ManyToManyField(to='App', blank=True, null=True, verbose_name='使用应用',related_name='kafka')
    class Meta:
        verbose_name_plural = "Kafka"
    def __str__(self):
        return self.ip.eth0_network+':'+self.port
        # return self.kafka_tag

#oss
class Oss(models.Model):
    login=models.ForeignKey(to='ALiCloud',blank=True, null=True, verbose_name='登录')
    apps=models.ManyToManyField(to='App', blank=True, null=True, verbose_name='相关应用',related_name='oss')
    backetname=models.ManyToManyField(to='BacketName', blank=True, null=True, verbose_name='BacketName')
    oss_tag = models.CharField(max_length=64, blank=True, null=True, verbose_name='标识')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    class Meta:
        verbose_name_plural = "Oss"
    def __str__(self):
        # from . import models as models_oss
        # print(models_oss.Oss.backetname.name)
        return self.oss_tag

class BacketName(models.Model):
    name=models.CharField(max_length=32,blank=True,null=True,verbose_name='BacketName')
    oss_auth_choices = ((1, '私有'),
                        (2, '公共读'),
                        (3, '公共写'),
                        )
    ossauth = models.SmallIntegerField(verbose_name='用户权限', choices=oss_auth_choices)
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    class Meta:
        verbose_name_plural = "BacketName"
    def __str__(self):
        return self.name


#mq
class Consumer(models.Model):
    title=models.CharField(max_length=32,blank=True,null=True,verbose_name='CID')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    class Meta:
        verbose_name_plural = "消费者"
    def __str__(self):
        return self.title

class Producer(models.Model):
    title=models.CharField(max_length=32,blank=True,null=True,verbose_name='PID')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    class Meta:
        verbose_name_plural = "生产者"
    def __str__(self):
        return self.title


class Topic(models.Model):
    title = models.CharField(max_length=32, blank=True, null=True, verbose_name='TopicID')
    producer = models.ManyToManyField(to='Producer', blank=True, null=True, verbose_name='生产者')
    consumer = models.ManyToManyField(to='Consumer', blank=True, null=True, verbose_name='消费者')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    class Meta:
        verbose_name_plural = "队列"
    def __str__(self):
        return self.title

class MqCase(models.Model):
    url = models.CharField(max_length=128, blank=True, null=True, verbose_name='链接')
    name = models.CharField(max_length=32, blank=True, null=True, verbose_name='实例名')
    region = models.CharField(max_length=16, blank=True, null=True, verbose_name='区域')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    class Meta:
        verbose_name_plural = "Mq实例"
    def __str__(self):
        return self.url

class RabbitMQ(models.Model):
    case=models.ForeignKey(to='MqCase',blank=True, null=True, verbose_name='RabbitMQ实例')
    mq_login=models.ForeignKey(to='ALiCloud',blank=True, null=True, verbose_name='登录')
    topic = models.ManyToManyField(to='Topic', blank=True, null=True, verbose_name='队列')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    apps=models.ManyToManyField(to='App', blank=True, null=True, verbose_name='相关应用',related_name='mq')
    class Meta:
        verbose_name_plural = "RabbitMQ"
    def __str__(self):
        return self.case.name


#redis

class Redis(models.Model):
    port=models.CharField(max_length=64, blank=True, null=True, verbose_name='端口',default='6379')
    password=models.CharField(max_length=128, blank=True, null=True, verbose_name='登录密码')
    url = models.CharField(verbose_name='链接',max_length=64, blank=True, null=True)
    redis_tag = models.CharField(max_length=1024, blank=True, null=True, verbose_name='标识')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    apps=models.ManyToManyField(to='App', blank=True, null=True, verbose_name='相关应用',related_name='redis')

    class Meta:
        verbose_name_plural = "Redis"
    def __str__(self):
        return self.url




#mysql
class MysqlLogin(models.Model):
    title = models.CharField(max_length=64, blank=True, null=True, verbose_name='授权账户')
    username = models.CharField(max_length=32, blank=True, null=True, verbose_name='用户名')
    password = models.CharField(max_length=128, blank=True, null=True, verbose_name='密码')
    mysql_auth_choices = ((1, 'ReadOnly'),
                        (2, 'ReadWrite'),
                        (3, 'root'),
                        )
    mysqlauth = models.SmallIntegerField(verbose_name='用户权限', choices=mysql_auth_choices)
    database=models.ManyToManyField(to='DataBase', blank=True, null=True, verbose_name='库名',related_name='logindatabase')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    class Meta:
        verbose_name_plural = "MysqlLogin"
    def __str__(self):
        return self.username

class Mysql(models.Model):
    url = models.CharField(max_length=64, blank=True, null=True, verbose_name='实例url')
    name = models.CharField(max_length=32, blank=True, null=True, verbose_name='实例名')
    hostname = models.CharField(max_length=32, blank=True, null=True, verbose_name='实例id')
    type = models.CharField(max_length=16, blank=True, null=True, verbose_name='数据库版本')
    cpu = models.IntegerField(max_length=4, blank=True, null=True, verbose_name='cpu')
    memory = models.IntegerField(blank=True, null=True, verbose_name='内存')
    iops = models.IntegerField( blank=True, null=True, verbose_name='IOPS')
    maxconnet = models.IntegerField( blank=True, null=True, verbose_name='最大连接数')
    maxstorage = models.CharField(max_length=16, blank=True, null=True, verbose_name='存储空间/G')
    usestorage = models.CharField(max_length=16, blank=True, null=True, verbose_name='使用空间/G')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    # mysql_login = models.ManyToManyField(to='MysqlLogin',blank=True, null=True, verbose_name='登录',related_name='mysqlcase')
    class Meta:
        verbose_name_plural = "Mysql实例"
    def __str__(self):
        return self.name


class DataBase(models.Model):
    name=models.CharField(max_length=64, blank=True, null=True, verbose_name='库')
    databases = models.ForeignKey(to='Mysql', blank=True, null=True, verbose_name='实例名', related_name='databasecase')
    class Meta:
        verbose_name_plural = "库"
    def __str__(self):
        return self.name

# class Mysql(models.Model):
#     case=models.ForeignKey(to='MysqlCase',verbose_name='实例',blank=True, null=True)
#     remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
#     port=models.CharField(max_length=8, blank=True, null=True, verbose_name='端口',default='3306')
#     mysql_login=models.ManyToManyField(to='MysqlLogin',blank=True, null=True, verbose_name='登录',related_name='mysql')
#     type_choices = ((1,'mysql'),
#                     (2,'mongodb'),
#                     )
#     type=models.SmallIntegerField(default=1,verbose_name='类型', choices=type_choices)
#     mysql_tag = models.CharField(max_length=1024, blank=True, null=True, verbose_name='标识')
#     class Meta:
#         verbose_name_plural = "Mysql"
#     def __str__(self):
#         return self.case.name



class Ftp(models.Model):
    username = models.CharField(max_length=64, blank=True, null=True, verbose_name='用户')
    password = models.CharField(max_length=64, blank=True, null=True, verbose_name='密码')
    path = models.CharField(max_length=64, blank=True, null=True, verbose_name='项目')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    class Meta:
        verbose_name_plural = "Ftp"
    def __str__(self):
        return self.username

class Svn(models.Model):
    path=models.CharField(max_length=64, blank=True, null=True, verbose_name='项目')
    remarks=models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    auth_choices = ((1, 'r'),
                    (2, 'rw'),
                    )
    svnauth = models.SmallIntegerField(verbose_name='权限', choices=auth_choices)
    groups=models.ManyToManyField(to='SvnGroup',blank=True, null=True,verbose_name='Svn组')
    class Meta:
        verbose_name_plural = "Svn"
    def __str__(self):
        return self.path



class SvnGroup(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True, verbose_name='组名')
    username = models.CharField(max_length=32, blank=True, null=True, verbose_name='用户')
    password = models.CharField(max_length=64, blank=True, null=True, verbose_name='密码')
    remarks = models.CharField(max_length=2048, blank=True, null=True, verbose_name='备注')
    class Meta:
        verbose_name_plural = "Svn用户组"
    def __str__(self):
        return self.name




class GitLab(models.Model):
    pass












