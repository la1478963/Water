
from django.contrib import admin
from rbac import models
#主机
admin.site.register(models.Lable)
admin.site.register(models.Memory)
admin.site.register(models.Disk)
admin.site.register(models.Os)
admin.site.register(models.Host)
# admin.site.register(models.Network)
admin.site.register(models.Source)
admin.site.register(models.Login)

#业务
admin.site.register(models.App)
# admin.site.register(models.AbroadPay)
# admin.site.register(models.CorePay)



#中间件
admin.site.register(models.ALiCloud)
admin.site.register(models.Zookeeper)
admin.site.register(models.Kafka)
admin.site.register(models.Oss)
admin.site.register(models.BacketName)
admin.site.register(models.Consumer)
admin.site.register(models.Producer)
admin.site.register(models.Topic)
admin.site.register(models.MqCase)
admin.site.register(models.RabbitMQ)
admin.site.register(models.Redis)
admin.site.register(models.MysqlLogin)
admin.site.register(models.DataBase)
# admin.site.register(models.MysqlCase)
admin.site.register(models.Mysql)
admin.site.register(models.Ftp)
admin.site.register(models.Svn)
admin.site.register(models.SvnGroup)


