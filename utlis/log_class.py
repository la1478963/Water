import  json
import logging
from django.conf import settings

# 既要把日志输出到控制台， 还要写入日志文件

'''
导入类后 
logger = Logger(request, loglevel=1, logger="fox").getlog()
日志输出
logger.error('error')
'''
class Logger():
    def __init__(self, loglevel, logger,num=0):
        '''
           指定保存日志的文件路径，日志级别，以及调用文件
           将日志存入到指定的文件中
        '''
        self.logname=settings.LOG_PATH[num]

        # 用字典保存日志级别
        self.format_dict = {
            1: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            2: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            3: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            4: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            5: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        }
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(self.logname)
        fh.setLevel(logging.DEBUG)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = self.format_dict[int(loglevel)]
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def getlog(self):
        return self.logger

