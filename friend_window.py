'''
@author: misterlihao
This is supposed to be main window
'''
import friend_list_item as FLI
import win32gui, win32api, win32con
import struct
from FriendList import FriendList
import threading
import online_check as oc
import message_transaction as mt
import queue
from WM_APP_MESSAGES import *

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
          WM_FRIENDREFRESHED: self.OnFriendRefreshed,
        }
        cn = self.RegisterClass()
        self.BuildWindow(cn)
        
        rect = win32gui.GetClientRect(self.hwnd)
        '''get friend list object'''
        self.friend_list = FriendList('friends')
        '''create list of child window'''
        self.friend_list_item_list = []
        '''for thread to insert new connections into
           and for main thread to get new connections from'''
        self.newconn_queue = queue.Queue()
        '''create child windows of friends'''
        for i in range(len(self.friend_list)):
            name = self.friend_list[i][1]
            ip = self.friend_list[i][0]
            fli = FLI.create(self, name, ip, 0, 24*i, rect[2], 24)
            self.friend_list_item_list.append(fli)
        
        win32gui.ShowWindow(self.hwnd, win32con.SW_NORMAL)
        '''begin responding to online checks from others'''
        myThread = threading.Thread(target=oc.ReceivingOnlineChecks)
        myThread.setDaemon(True)
        myThread.start()
        '''begin accepting connections to chat''' 
        myThread = threading.Thread(target=mt.ReceivingConnections, args=(self.OnConnAcceptInThread,))
        myThread.setDaemon(True)
        myThread.start()
        '''begin refreshing online status'''
        myThread = threading.Thread(target=self.RefreashFriendStatusInThread)
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
        '''this is supposed to be called in thread
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
        
        friend_list_item = None
        for fli in self.friend_list_item_list:
            if fli.IsMe(addr[0]):
                friend_list_item = fli
        
        print('user', friend_list_item.model.friend_name, 'connected at', addr)
        friend_list_item.StartChat(sock)
    
    def RefreashFriendStatusInThread(self):
        while True:
            time.sleep(1)
            self.updated_friends = self.friend_list.RefreshOnlineStatus()
            if len(self.updated_friends) > 0:
                win32gui.SendMessage(self.hwnd, WM_FRIENDREFRESHED, 0, 0)
    
    def OnFriendRefreshed(self, hwnd, msg, wp, lp):    
        for index in self.updated_friends:
            friend_list_item = self.friend_list_item_list[index]
            friend_list_item.model.online = not friend_list_item.model.online
            win32gui.InvalidateRect(friend_list_item.hwnd, (FLI.online_indicate_rect),True)
        
    def OnDestroy(self, hwnd, msg, wp, lp):
        win32gui.PostQuitMessage(0)
        print(self.friend_list_item_list)
        for each in self.friend_list_item_list:
            try:
                each.edit_window.destroy()
                each.edit_window.quit()
            except:pass
        self.friend_list.Save()
        return True



import time
if __name__ == '__main__':
    mainwin = FriendWin()
    
    '''play as a remote user to test recving functions'''
    def test(*args):
        pass
        
    th=threading.Thread(target=test)
    th.setDaemon(True)
    th.start()
    
    # end win32 windows
    win32gui.PumpMessages()
    print('end')
