#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os   #Python的标准库中的os模块包含普遍的操作系统功能  
import re   #引入正则表达式对象  
import urllib   #用于对URL进行编解码  
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler  #导入HTTP处理相关的模块  
import socket
import time


#自定义处理程序，用于处理HTTP请求  
class TestHTTPHandler(BaseHTTPRequestHandler):

    def get_host_info(self):
        self.client_ip = self.client_address[0]
        #获取本机ip
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            self.local_ip = s.getsockname()[0]
        finally:
            s.close()
        # 本机hostname
        self.hostname = socket.gethostname()
        self.app_name = 'first-application'
        self.app_port = '8811'
        self.app_start = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

    #处理GET请求  
    def do_GET(self):
        self.get_host_info()
        #获取URL
        print 'URL=',self.path
        #页面输出模板字符串  
        templateStr = '''
        <html>
        <head>
        <meta charset="utf-8"> 
        <title>TEST</title>
        <style>
        table, td, th
        {
        	border:1px solid green;
                margin:50 auto
        }
        th
        {
        	background-color:green;
        	color:white;
        }
        .td_right { 
        text-align:right; 
        padding-right: 10px;
        }
        .td_left { 
        text-align:left; 
        padding-left: 10px;
        }
        </style>
        </head>
        <body>
        <table>
        <tr>
        <th>字段</th>
        <th>值</th>
        </tr>
        <tr><td class='td_right'>主机名: </td><td class='td_left'>%s</td></tr>
        <tr><td class='td_right'>本机IP: </td><td class='td_left'>%s</td></tr>
        <tr><td class='td_right'>应用名: </td><td class='td_left'>%s</td></tr>
        <tr><td class='td_right'>应用端口: </td><td class='td_left'>%s</td></tr>
        <tr><td class='td_right'>应用启动时间: </td><td class='td_left'>%s</td></tr>
        </table>
        </body>
        </html>
        '''
        templateStr = templateStr % (self.hostname, self.local_ip, self.app_name, self.app_port, self.app_start)

        self.protocal_version = 'HTTP/1.1'  #设置协议版本  
        self.send_response(200) #设置响应状态码  
        self.send_header("Welcome", "Contect")  #设置响应头  
        self.end_headers()
        self.wfile.write(templateStr)   #输出响应内容  

        #启动服务函数  
def start_server(port):
        http_server = HTTPServer(('', int(port)), TestHTTPHandler)
        http_server.serve_forever() #设置一直监听并接收请求  

#os.chdir('static')  #改变工作目录到 static 目录  
start_server(8811)  #启动服务，监听8000端口
