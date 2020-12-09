#coding=utf-8
import socket
#获取本机电脑名
host_name = socket.getfqdn(socket.gethostname(  ))
host_name = socket.gethostname()


def get_host_ip():
    #获取本机ip
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

host_ip = get_host_ip()
print(host_ip)
print(host_name)
