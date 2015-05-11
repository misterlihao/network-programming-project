'''
@author: misterlihao
This is supposed to be main window
'''
import friend_list_item
import win32gui, win32api, win32con
import struct
from FriendList import FriendList
import threading
import online_check as oc
import message_transaction as mt
import queue
WM_CONNACCEPTED = win32con.WM_APP+1
WM_CHATMSGRECV = win32con.WM_APP+2



class FriendWin:
    '''
    the main window
    main control of the whole program
    '''
    def __init__(self): 
        win32gui.InitCommonControls()
        self.hinst = win32api.GetModuleHandle(None)
        self.message_map = {
          win32con.WM_DESTROY: self.OnDestroy,
          win32con.WM_SYSCOMMAND: self.OnSysCommand,
          WM_CONNACCEPTED: self.OnConnAccepted,
          WM_CHATMSGRECV: self.OnChatMessageReceived,
        }
        cn = self.RegisterClass()
        self.BuildWindow(cn)
        
        rect = win32gui.GetClientRect(self.hwnd)
        self.friend_list = FriendList('friends')
        self.friend_list_item_list = []
        self.newconn_queue = queue.Queue()
        self.chatmsg_queue = queue.Queue()
        for i in range(len(self.friend_list)):
            name = self.friend_list[i][1]
            ip = self.friend_list[i][0]
            fli = friend_list_item.create(self.hwnd, name, ip, 0, 24*i, rect[2], 24)
            self.friend_list_item_list.append(fli)
        
        win32gui.ShowWindow(self.hwnd, win32con.SW_NORMAL)
        
        self.sockList = []
        myThread = threading.Thread(target=oc.ReceivingOnlineChecks)
        myThread.setDaemon(True)
        myThread.start()
        myThread = threading.Thread(target=mt.ReceivingConnections, args=(self.OnConnAcceptInThread,))
        myThread.setDaemon(True)
        myThread.start()
        
    def RegisterClass(self):
        className = "friend_window"
        wc = win32gui.WNDCLASS()
        wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wc.lpfnWndProc = self.message_map
        wc.cbWndExtra = 0
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32con.COLOR_WINDOW + 1
        wc.hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        wc.lpszClassName = className
        wc.cbWndExtra = win32con.DLGWINDOWEXTRA + struct.calcsize("Pi")
        win32gui.RegisterClass(wc)
        return className

    def BuildWindow(self, className):
        style = win32con.WS_OVERLAPPED|win32con.WS_CAPTION|win32con.WS_SYSMENU|win32con.WS_MINIMIZEBOX
        w=200; h=500
        self.hwnd = win32gui.CreateWindow(
                             className,
                             "freind list", style,
                             win32con.CW_USEDEFAULT,
                             win32con.CW_USEDEFAULT,
                             w,h,0,0,self.hinst,None)
        
    def OnSysCommand(self, hwnd, msg, wp, lp):
        '''win32 callback, edit to control
        minimized, maximized and so on'''
        
        '''
        if wp == win32con.SC_MINIMIZE:
            win32gui.ShowWindow(self.hwnd, 0)
            time.sleep(2)
            win32gui.ShowWindow(self.hwnd, 1)
            return True
        '''
        return win32gui.DefWindowProc(hwnd, msg, wp, lp)
    
    def OnConnAcceptInThread(self, sock, addr):
        '''this is supposted to be called in thread
        designed to be call back of 
        message_transaction.ReceivingConnections'''
        self.newconn_queue.put((sock, addr))
        win32gui.SendMessage(self.hwnd, WM_CONNACCEPTED, 0, 0)
        
    def OnConnAccepted(self, hwnd, msg, wp, lp):
        '''
        win32 callback
        manage the connection stored in self.newconn_queue
        be aware of that the order of connection may not be ordered by time
        '''
        sock, addr = self.newconn_queue.get()
        self.sockList.append(sock)
        
        friend_list_item = None
        for fli in self.friend_list_item_list:
            if fli.IsMe(addr[0]):
                friend_list_item = fli
        
        myThread = threading.Thread(target= self.listen_to_chat_messagesInThread, 
                args=(sock, self.friend_list_item_list.index(fli)))
        myThread.setDaemon(True)
        myThread.start()
        
        print('user ', self.friend_list_item_list.index(fli), ' connected')
        friend_list_item.StartChat()
        print(addr)
    
    def listen_to_chat_messagesInThread(self, *args):
        '''
        pre porcess messages in this function
        maybe unpack your message here 
        (if it was packed to ensure the completeness) 
        '''
        print('begin  recving')
        sock, friend_index = args
        while True:
            try:
                msg = sock.recv(1000)
                if msg == b"":
                    raise Exception()
            except:
                print('recv fail')
                return
            msg = msg.decode('utf8')
            '''send the message here.Control it here'''
            self.chatmsg_queue.put((friend_index, msg))
            win32gui.SendMessage(self.hwnd, WM_CHATMSGRECV, 0, 0)
        
    def OnChatMessageReceived(self, hwnd, message, wp, lp):
        friend_index, msg = self.chatmsg_queue.get()
        self.friend_list_item_list[friend_index].OnChatMessageReceived(msg)
    
    def OnDestroy(self, hwnd, msg, wp, lp):
        win32gui.PostQuitMessage(0)
        return True

import time
if __name__ == '__main__':
    mainwin = FriendWin()
    
    '''play as a remote user to test recving functions'''
    def test(*args):
        time.sleep(1)
        sock = mt.StartTalking('127.0.0.1')
        sock.send('123'.encode('utf8'))
        sock.send('456'.encode('utf8'))
        
    th=threading.Thread(target=test)
    th.setDaemon(True)
    th.start()
    
    # end win32 windows
    win32gui.PumpMessages()
    print('end')