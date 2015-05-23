import socket
import threading
import myPacket as mp

def StartTalking(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    s.settimeout(1)
    try:
        s.connect((ip, 12347))
    except:
        print('Connect socket fail.')
        return None
    
    s.settimeout(None)
    return s

def ReceivingConnections(*after_accept):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)  
    s.bind(('', 12347))  
    s.listen(20)
    while(1):
        conn, address = s.accept()
        after_accept[0](conn, address);
    s.close()

def SendMessageAndAnime(s, message, anime):
    '''can send None-text pkg'''
    mp.sendPacket(s, message.encode('utf8'))
    mp.sendPacket(s, anime.encode('utf8'))

def RecvMessageAndAnime(s):
    '''return a tiple:(message, anime)'''
    message = mp.recvPacket(s).decode('utf8')
    anime = mp.recvPacket(s).decode('utf8')
    return message, anime

global_socket = None

'''
""""""""""
"try code"
""""""""""
def trySocket():
    global global_socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)  
    s.bind(('127.0.0.1', 12348))  
    s.listen(2)
    while(1):
        conn, address = s.accept()
        print(RecvMessageAndAnime(conn))
    s.close()
myThread = threading.Thread(target = trySocket)
myThread.start()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 12348))
message = ''
anime = ''
SendMessageAndAnime(s, message, anime)
print(RecvMessageAndAnime(s))
'''