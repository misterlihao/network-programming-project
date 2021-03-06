import wait_socket_messages as wsm
import socket

check_online_ip='127.0.0.1'
check_online_port=12346
check_online_type='TCP'

def ReceivingOnlineChecks():
    global check_online_ip
    global check_online_port
    global check_online_type
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)  
    s.bind(('', 12346))  
    s.listen(10) 
    while(1):
        conn, address = s.accept()
        try:
            pass
        except Exception as e:
            print('ReceivingOnlineChecks:', e)
        conn.close()
    s.close()
    
def CheckSomeoneOnline(ip):
    global check_online_ip
    global check_online_port
    global check_online_type
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    try:
        s.settimeout(0.5)
        s.connect((ip, check_online_port))
    except:
        s.close()
        return False
    finally:
        s.settimeout(None)
        
    s.close()
    return True
