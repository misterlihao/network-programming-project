import socket
import threading
import image_window as iw

def StartTalking(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    try:
        s.connect((ip, 12347))
    except:
        print('Connect socket fail.')
    return s

def ReceivingConnections():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)  
    s.bind(('127.0.0.1', 12347))  
    s.listen(20)
    while(1):
        conn, address = s.accept()
        myThread = threading.Thread(target = ReceivingMessagesFrom, args=(conn,))
        myThread.setDaemon(True)
        myThread.start()
    s.close()

def ReceivingMessagesFrom(*arg):
    conn,=arg
    while(1):
        try:  
            conn.settimeout(5)  
            buf = conn.recv(1024)
            print(buf.decode('ascii'))
            #show_message  
            #conn.send('welcome to server!')  
        except :  
            print ('time out') 
         
    conn.close()

def StartRecvMessage():
    '''wait_for_message'''