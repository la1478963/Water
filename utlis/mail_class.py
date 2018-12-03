import smtplib
from email.mime.text import MIMEText


class SendMail(object):
    def __init__(self,mailto_list):
        self.mail_host = "smtp.163.com" #使用的邮箱的smtp服务器地址，这里是163的smtp地址
        self.mail_user = "m13718098481"         #用户名
        self.mail_pass="Leon1478963"           #密码
        self.mail_postfix="163.com"             #邮箱的后缀，网易就是163.com
        self.mailto_list=mailto_list            #收件人(列表)

    def send_mail(self,to_list,sub,content):
        me="hello"+"<"+self.mail_user+"@"+self.mail_postfix+">"
        msg = MIMEText(content,_subtype='plain')
        msg['Subject'] = sub
        msg['From'] = me
        msg['To'] = ";".join(to_list)                #将收件人列表以‘；’分隔
        try:
            server = smtplib.SMTP()
            server.connect(self.mail_host)                            #连接服务器
            server.login(self.mail_user,self.mail_pass)               #登录操作
            server.sendmail(me, to_list, msg.as_string())
            server.close()
            return True
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    mailto_list=['350608119@qq.com']
    sm_obj=SendMail(mailto_list)
    for i in range(len(mailto_list)):            #发送1封，上面的列表是几个人，这个就填几
        if sm_obj.send_mail(mailto_list,"服务器到期预警",
                            "电话是XXX"):  #邮件主题和邮件内容
            #这是最好写点中文，如果随便写，可能会被网易当做垃圾邮件退信
            print ("done!")
        else:
            print ("failed!")

