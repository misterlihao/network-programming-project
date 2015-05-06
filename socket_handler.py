import socket

def CreatePort(type, ip, port):
    if type == 'TCP':
        sock_type=socket.SOCK_STREAM
    else: sock_type=socket.SOCK_DGRAM
    
    s=socket.socket(socket.AF_INET,sock_type)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    s.bind((ip, port))
    return s