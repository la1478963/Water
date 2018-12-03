import jenkins
import time
import sys
import requests
#python jenkins_demo admin-test
res_url=''
jenkins_server_url='http://192.168.52.5:9988/jenkins/'
job_name=  sys.argv[0]  if  sys.argv[0] else  'admin-test-compile'
user_id='admin'
password='admin'
build_num = sys.argv[1] if sys.argv[1] else False

server=jenkins.Jenkins(jenkins_server_url,username='admin',password='admin')
res_data='ERROR:build error'


while build_num:
    #build - job
    server.build_job(job_name)
    time.sleep(5)
    get_num=server.get_job_info(job_name)['lastBuild']['number']
    if build_num == get_num:
    # print('本次的构建号:'+str(num))
        time.sleep(1)
        if server.get_build_info(job_name, get_num).get('result'):
            res_data=server.get_build_console_output(job_name,get_num)
            break

# res_all=server.get_build_console_output(job_name,num)

# print(server.get_jobs())

# print(server.get_view_config(job_name))
# print(server.get_plugins_info())

#返回数据
requests.post(res_url,data=res_data)






