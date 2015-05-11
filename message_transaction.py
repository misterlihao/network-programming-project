import socket
import threading

def StartTalking(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    s.settimeout(1)
    try:
        s.connect((ip, 12347))
    except:
        print('Connect socket fail.')
    s.settimeout(None)
    return s

def ReceivingConnections(*after_accept):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)  
    s.bind(('127.0.0.1', 12347))  
    s.listen(20)
    while(1):
        conn, address = s.accept()
        after_accept[0](conn, address);
    s.close()
