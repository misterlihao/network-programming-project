import threading
import online_check as oc
import friend_mechanism as fm


check_online_ip='127.0.0.1'
check_online_port=12345
check_online_timeout=2
check_online_type='TCP'
friend_file='friends'
friend_list=[]

def Online():
    global friend_list
    global friend_file
    
    try:
        friend_list=fm.ReadFriendList(friend_file)
    except:
        pass
    '''    
    s = CreatePort(check_online_type, check_online_ip, check_online_port, check_online_timeout)
    threading.Thread(target=ReceivingOnlineChecks, args=(s)).start()
    friend_list=RefreshOnlineFriends(friend_list)#refreshing and broadcast
    threading.Thread(target=StartRecvMessage).start()#write it when doing "receiving message" function
    '''
    print(friend_list)

def Offline():
    global friend_list
    global friend_file
    
    fm.WriteFriendList(friend_file, friend_list)
    
    
Online()
Offline()