# 导入socket库:
import socket
import threading
import time


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def tcplink(sock, addr):
    print('Accept new connection from %s:%s...' % addr)
    try:
        sock.send(b'Welcome!')
        while True:
            try:
                data = sock.recv(1024)
                time.sleep(1)
                if not data or data.decode('utf-8') == 'exit':
                    break
                sock.send(('Hello, %s!' % data.decode('utf-8')).encode('utf-8'))
            except ConnectionError as e:
                print(f'Connection error with {addr}: {e}')
                break
            except Exception as e:
                print(f'Error occurred with {addr}: {e}')
                break
    finally:
        sock.close()
        print('Connection from %s:%s closed.' % addr)
    sock.close()
    print('Connection from %s:%s closed.' % addr)


# 监听端口:
s.bind(('127.0.0.1', 9999))
s.listen(5)
print('Waiting for connection...')

while True:
    # 接受一个新连接:
    sock, addr = s.accept()
    # 创建新线程来处理TCP连接:
    t = threading.Thread(target=tcplink, args=(sock, addr))
    t.start()
