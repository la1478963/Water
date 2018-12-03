import time, datetime
from utlis.log_class import Logger
from django.forms.boundfield import BoundField

class Time(object):
    logger = Logger(loglevel=1, logger="fox").getlog()
    @staticmethod
    def t_to_stamp(t):
        '''时间格式转变为时间戳'''
        try:
            timestamp_dt = time.strptime(t, '%Y-%m-%d %H:%M:%S')
        except TypeError as e:
            Time.logger.error('time_class.t_to_stamp'+str(e))
            return 'ERROR'
        stamp = int(time.mktime(timestamp_dt))
        return stamp

    @staticmethod
    def stamp_to_t(st):
        '''时间戳变为时间'''
        try:
            timeArray = time.localtime(int(st))
        except TypeError as e:
            Time.logger.error('time_class.stamp_to_t'+str(e))
            return 'ERROR'
        otherStyleTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
        return otherStyleTime

    @classmethod
    def time_func(cls,t):
        return 'T'.join(t.split(' ')) + 'Z'


    @classmethod
    def ali_def_monitor(cls):
        #默认都会多减去一分钟，因为阿里云检测到描述不是00 自动会增加1分钟
        #UTC时间 需要 我们的时间减去8小时
        utc=8
        nowTime = datetime.datetime.now()
        endTime = (nowTime - datetime.timedelta(minutes=1,hours=utc)).strftime('%Y-%m-%d %H:%M:%S')  # 过去一分钟(当做现在)
        startTime = (nowTime - datetime.timedelta(hours=utc, minutes=6)).strftime('%Y-%m-%d %H:%M:%S')  # 过去一小时

        start_time=cls.time_func(startTime)
        end_time=cls.time_func(endTime)

        return (start_time,end_time)

# A=jiami()
# B=A.base_str_encrypt('hello')
# print(B)
# print(A.base_str_decrypt(B))
