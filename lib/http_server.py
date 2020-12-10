# coding:utf-8
import subprocess as commands
import time
import os
import shutil
import sys
import datetime
import json
import random
#### python3 ##########
# from urllib.parse import urlparse
# from http.server import BaseHTTPRequestHandler, HTTPServer,CGIHTTPRequestHandler
#### python2 ##########
import urlparse
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import commands

#######################
# 参数配置
HTTP_PORT = 8880  # 默认服务端口
WORK_PATH = '/export/imageServer/'  # 工作目录
LOG_SAVE = True  # 是否将log保存到文件
LOG_NAME = '/var/log/first-application.log'  # 访问日志
MultiThreading = True  # 开启多线程
tokenCheck = {
    'check': False,  # 开启token验证
    'token': ['xxxxxxxxx', 'test-token']
}
allowIP = ['xxxxxxxxxx']
# 导入外部配置
try:
    from http_conf import *
except:
    pass

###################
HTTP_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else HTTP_PORT
# 创建目录
if not os.path.exists(WORK_PATH):
    os.mkdir(WORK_PATH)




#######################

class HttpHandler(BaseHTTPRequestHandler):
    # 处理GET请求
    def do_GET(self):
        self.resolve_request()
        success, code, data = self.check_request()
        if not success:
            self.log_error(data)
            self.my_responses(code, data)
            return
        if self.request_path == '/first-application':
            code = 200
            data = {'code': code, 'msg': 'success'}
            self.my_responses(code, data)
        else:
            code = 200
            data = {'code': code, 'msg': 'not allow'}
            self.my_responses(code, data)

        if self.request_path == '/':
            code = 200
            data = {'code': code, 'msg': 'success'}
            self.my_responses(code, data)
        else:
            # 下载文件
            fp = self.format_path(WORK_PATH, '1') + self.format_path(self.path, '1')
            if os.path.isfile(fp):
                self.log_info('[Request Download] %s' % fp)
                f = open(fp, 'rb')
                fs = os.fstat(f.fileno())
                self.send_response(200)
                self.send_header("Content-type", "application/octet-stream; charset=utf-8")
                self.send_header("Content-Length", str(fs[6]))
                self.end_headers()
                self.wfile.write(f.read())
                self.log_info('[Download Success] %s' % fp)
                return
            else:
                code = 404
                if os.path.isdir(fp):
                    data = {'code': '-1', 'msg': '[%s]文件夹，无法下载' % fp}
                else:
                    data = {'code': '-1', 'msg': '[%s]文件不存在' % fp}
                self.my_responses(code, data)
                self.log_error('[Download Error] %s %s' % (fp, json.dumps(data, ensure_ascii=False)))
                return

    # 处理POST消息
    def do_POST(self):
        self.resolve_request()
        success, code, data = self.check_request()
        if not success:
            self.log_error(data)
            self.my_responses(code, data)
            return
        if self.request_path == '/':
            code = 200
            data = {'code': code, 'msg': 'success'}
            self.my_responses(code, data)
        elif self.request_path == '/status/':
            print(self.request_parse)
            self.Handel_task('status')
        else:
            code = 404
            data = {'code': code, 'msg': u'路径不存在'}
            self.my_responses(code, data)

    def Handel_task(self, method):
        if method == 'status':
            code = 200
            data = {'code': code, 'msg': 'success22'}
            # 获取url参数
            print(self.request_parse)
            # 获取post数据
            print(self.request_data)
            # 相应json
            self.my_responses(code, data)

    # 白名单/token检测
    def check_request(self):
        # token检查
        if tokenCheck['check']:
            if not self.request_token in tokenCheck['token']:
                code = 401
                data = {'code': -1, 'msg': 'token check error'}
                return (False, code, data)
        # ip 黑白名单检测
        client_ip = self.client_address[0]
        code = 200
        data = {'code': -1, 'msg': '%s is refused' % client_ip}
        if not client_ip in allowIP:
            #return (False, code, data)
            return (True, code, data)
        return (True, 200, '')

    # 解析request参数
    def resolve_request(self):
        # 自定义task_id
        self.task_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + str(random.randint(1000, 9999))

        # 提取token
        self.request_token = self.headers.get('token', 'xxxxx')

        # 提取content_type
        content_type = self.headers.get('Content-Type', 'application/x-www-form-urlencoded').lower().split(';')[0]
        if content_type == 'application/json':
            self.content_type = 'json'
        elif content_type in ['application/x-www-form-urlencoded', 'multipart/form-data']:
            self.content_type = 'form'
        else:
            self.content_type = 'json'

        # 提取url path
        self.request_path = self.format_path(self.path)
        self.request_path_list = [i for i in self.request_path.split('/') if i != '']

        # 提取url parse
        query = urlparse.urlparse(self.path).query
        self.request_parse = None
        if urlparse.parse_qs(query).items():
            self.request_parse = dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])

        # 提取post的data
        self.request_data = None
        if self.command == 'POST':
            if self.content_type == 'json':
                length = int(self.headers['content-length'])
                datas = self.rfile.read(length)
                self.request_data = json.loads(datas.decode("utf-8"))

        log_data = {
            'token': self.request_token,
            'command': self.command,
            'content_type': self.content_type,
            'path': self.request_path,
            'path_list': self.request_path_list,
            'parse': self.request_parse,
            'data': self.request_data
        }
        self.log_info('[Request Data] %s' % log_data)

    # 解析request路径
    def format_path(self, url, rtype=None):
        if not url:
            return None
        query = urlparse.urlparse(url).path
        if not rtype:
            # 输出'/'结尾的path; eg: '/sn/xxx.xml/'
            if query[-1:] != '/':
                query = query + '/'
        elif rtype == '1':
            # 输出无'/'结尾的path; eg: '/sn/xxx.xml'
            if query[-1:] == '/':
                query = query[0: -1]
        elif rtype == '2':
            if query[0] != '/':
                query = '/' + query
            if query[-1:] == '/':
                query = query[0: -1]
            # 输出'/'开头的，并且无'/'结尾的path; eg: '/sn/xxx.xml'
        return query

    def get_path_name(self, path):
        if path[-1] == '/':
            path = path[0:-1]
        file_dir = path.split('/')[0:-1]
        file_dir = [i for i in file_dir if i != '']
        file_dir = '/'.join(file_dir)
        file_name = path.split('/')[-1]
        return (file_dir, file_name)

    def file_check(self, file, md5, size):
        result = True
        if FILE_CHECK['md5'] and md5:
            self.log_info('[Upload Check] MD5 Checking')
            cmd = 'md5sum %s' % file
            (status, output) = commands.getstatusoutput(cmd)
            self.log_info('[Upload Check] Real MD5 %s' % output)
            if output.split()[0] != md5:
                result = False
                self.log_error('[Upload Check] MD5 Error')

        if FILE_CHECK['size'] and size:
            self.log_info('[Upload Check] Size Checking')
            cmd = 'ls -l %s |awk \'{print $5}\'' % file
            (status, output) = commands.getstatusoutput(cmd)
            self.log_info('[Upload Check] Real Size %s' % output)
            if output != size:
                result = False
                self.log_error('[Upload Check] Size Error')
        return result

    # json格式的http响应
    def my_responses(self, code, data):
        enc = "UTF-8"
        self.send_response(code)
        self.send_header("Content-type", "application/json; charset=%s" % enc)
        self.end_headers()
        json_string = json.dumps(data, ensure_ascii=False, encoding='utf-8')
        self.wfile.write(json_string)

    def log_date_time_string(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    def log_message(self, format, *args):
        mylog = '[%s] [%s] [%s] %s\n' % (
            self.log_date_time_string(),
            self.client_address[0],
            self.task_id,
            format % args
        )
        # 输出到console
        sys.stderr.write(mylog)
        # 保存到log文件
        if LOG_SAVE:
            # 创建日志目录
            LOG_PATH = WORK_PATH + 'myhttp_log/'
            if not os.path.exists(LOG_PATH):
                os.mkdir(LOG_PATH)
            stime = datetime.datetime.now().strftime('%Y%m%d')
            with open(LOG_NAME, 'a+') as f:
                f.write(mylog)

    def log_info(self, data):
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)
        data = '[INFO] %s' % data
        self.log_message(data)

    def log_error(self, data):
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)
        data = '[ERROR] %s' % data
        self.log_message(data)

    def ScriptWorker(self, script):
        # 执行脚本，返回状态码和输出
        (status, result) = commands.getstatusoutput(script)
        # 如果成功返回200，如果失败返回400
        if status == 0:
            self.send_response(200)
        else:
            self.send_response(400)


def main(port=None, workdir=None):
    # 自定义端口和路径
    server_address = ('0.0.0.0', HTTP_PORT)
    if MultiThreading:
        http_server = MultiThreadingServer(server_address, HttpHandler)
        t_type = 'Multi-Thread'
    else:
        http_server = HTTPServer(server_address, HttpHandler)
        t_type = 'Single-Thread'

    print('Starting server: %s' % t_type)
    print('Listen PORT: %s' % HTTP_PORT)
    print('Work Path: %s' % WORK_PATH)
    http_server.serve_forever()


class MultiThreadingServer(ThreadingMixIn, HTTPServer):
    pass


if __name__ == '__main__':
    main()
