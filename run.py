# coding=utf-8
import SocketServer
import SimpleHTTPServer

PORT=8811

Handler=SimpleHTTPServer.SimpleHTTPRequestHandler

# 解决端口不立即释放问题
SocketServer.TCPServer.allow_reuse_address=True

httpd=SocketServer.TCPServer(('',PORT),Handler)

print('server at port',PORT)

httpd.serve_forever()
