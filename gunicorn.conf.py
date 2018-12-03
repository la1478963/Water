import multiprocessing
bind = "0.0.0.0:8081"
workers = 3
errorlog = './log/gunicorn.error.log'
#accesslog = './gunicorn.access.log'
#loglevel = 'debug'
proc_name = 'gunicorn_blog_project'