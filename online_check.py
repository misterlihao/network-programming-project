import wait_socket_messages as wsm
import socket_handler as sh
import socket

def ReceivingOnlineChecks(ready_socket):
    while(1):
        check, from_who = ready_socket.recvfrom(10)
        ready_socket.sendto(b'Online',(from_who, check_online_port))
        ready_socket.close()
    pass
    
def CheckSomeoneOnline(ip):
    s = sh.CreatePort(check_online_type, check_online_ip, check_online_port, check_online_timeout)
    try:
        s.connect(ip, check_online_port)
    except:
        s.close()
        return False
    
    s.close()
    return True
    
def StartRecvMessage():
    '''wait_for_message'''