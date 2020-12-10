# coding:utf-8
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from lib.http_server import HttpHandler
import commands
import subprocess
import os
import socket


HTTP_PORT = 8811  # 默认服务端口
WORK_PATH = '/export/imageServer/'  # 工作目录
MultiThreading = True

class myserver(HttpHandler):
    def runcmd(self, cmd):
        print(cmd)
        p = subprocess.Popen(cmd,shell=True, close_fds=True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        result = p.stdout.read().decode("utf-8", "ignore").replace('\n', '')
        return result

    def get_host_ip(self):
        #获取本机ip
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    def do_GET(self):
        ip = self.get_host_ip()
        client_ip = self.client_address[0]
        print(ip)
        print(client_ip)
        self.resolve_request()
        success, code, data = self.check_request()
        if not success:
            self.log_error(data)
            self.my_responses(code, data)
            return
        if self.request_path == '/':
            msg='APP is  Running'
        elif self.request_path == '/first-application/ip/':
            msg={'app_ip': ip} 
        else:
            msg='APP is  Running'
        code = 200
        data = {'code': code, 'msg': msg}
        import time
        self.my_responses(code, data)

    def do_POST(self):
        self.resolve_request()
        success, code, data = self.check_request()
        print(success, code, data)
        # 关闭post
        if True:
            code = 200
            data = {'code': code, 'msg': 'post is off'}
            self.my_responses(code, data)       
        if not success:
            self.log_error(data)
            self.my_responses(code, data)
            return
        if self.request_path == '/':
            code = 200
            data = {'code': code, 'msg': 'success'}
            self.my_responses(code, data)
        elif self.request_path == '/task/':
            code = 200
            data = {'code': code, 'msg': 'success'}
            operate = self.request_data['operate']
            if operate == 'start_nc':
                port = self.request_data['data']['port']
                imgName = self.request_data['data']['imgName']
                cmd = 'bash ./startNC.sh %s %s   ' % (port, imgName)
                result = self.runcmd(cmd)
                if 'success' in result:
                    code = 0
                else:
                    code = 1
                data = {'code': code, 'msg': result}
                self.log_info(data)
            if operate == 'image_init':
                img_name = self.request_data['data']['img_name']
                root_disk = self.request_data['data']['root_disk']
                IPADDR = self.request_data['data']['IPADDR']
                hostname = self.request_data['data']['hostname']
                cmd = 'bash ./do_iaas_init.sh %s %s %s %s  ' % (img_name, root_disk, IPADDR, hostname)
                result = self.runcmd(cmd)
                if 'success' in result:
                    code = 0
                else:
                    code = 1
                data = {'code': code, 'msg': result}
            if operate == 'image_import':
                import_data = self.request_data['data']
                self.log_info('import into ceph: %s' % import_data)
                volumes = self.request_data['data']['volumes']
                success, result = sendTask(import_data)
                if success:
                    self.log_info('import into ceph result: %s' % result)
                    code = 0
                    # 删除迁移成功的raw
                    for tdisk in volumes:
                        delefile = tdisk['image_file']
                        if os.path.exists(delefile):
                            os.remove(delefile)
                            self.log_info('Delete [%s] Success' % delefile)
                else:
                    self.log_error('import into ceph result: %s' % result)
                    code = 1
                data = {'code': code, 'msg': result}
            self.my_responses(200, data)
        else:
            code = 404
            data = {'code': code, 'msg': u'路径不存在'}
            self.my_responses(code, data)
class MultiThreadingServer(ThreadingMixIn, HTTPServer):
    pass
def main(port=None, workdir=None):
    # 自定义端口和路径
    server_address = ('0.0.0.0', HTTP_PORT)
    if MultiThreading:
        http_server = MultiThreadingServer(server_address, myserver)
        t_type = 'Multi-Thread'
    else:
        http_server = HTTPServer(server_address, myserver)
        t_type = 'Single-Thread'

    print('Starting server: %s' % t_type)
    print('Listen PORT: %s' % HTTP_PORT)
    print('Work Path: %s' % WORK_PATH)
    http_server.serve_forever()    
if __name__ == '__main__':
    main()
