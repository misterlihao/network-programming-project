'''
@author: misterlihao
This is supposed to be main window
'''
import mailHandle
from synchronizationRole import updataIfNeed
import friend_list_item as FLI
import win32gui, win32api, win32con
import struct
from FriendList import FriendList
import threading
import online_check as oc
import message_transaction as mt
import myPacket as mp
import queue
import socket
from WM_APP_MESSAGES import *
import check_online_window as COW
import tkinter as tk
from distutils.cmd import Command
from test.test_heapq import SideEffectLT
from tkinter.tix import COLUMN
from tkinter.constants import BOTH
from image_window import image_window
from time import sleep
import mailHandle as mh
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
          win32con.WM_COMMAND: self.OnCommand,
          win32con.WM_MOUSEWHEEL: self.OnMouseWheel,
          win32con.WM_SIZE: self.OnSize,
          WM_CONNACCEPTED: self.OnConnAccepted,
          WM_FRIENDREFRESHED: self.OnFriendRefreshed,
        }
        '''we default to use character 1'''
        self.char_id = '1'
        '''Login email GUI here to get user's email'''
        '''if login success, return my email address to self.email'''
        self.email = 'default@gmail.com'
        self.email_passwd = ''
        try:
            with open('acpwd.txt') as file:
                for line in file:
                    acpwd = line.split(':')
                    self.email = acpwd[0]
                    self.email_passwd = acpwd[1]
                    print(acpwd)
                    self.startCheckEmail()
        except:
            OpenLogInWindow(self)
        '''get friend list object'''
        self.friend_list = FriendList('friends')
        '''storage of mails'''
        self.friend_new_mails = [[]for f in self.friend_list]
        '''create list of child window'''
        self.friend_list_item_list = []
        '''for thread to insert new connections into
           and for main thread to get new connections from'''
        self.newconn_queue = queue.Queue()
        '''friend switch online status'''
        self.updated_friends = []
        '''index of frist friend in self.friend_list'''
        self.friend_first_index = 0
        '''index of frist friend in self.friend_list'''
        self.friend_list_len = 4
        '''chat windows'''
        self.chat_wins = []
        '''create child windows of friends'''
        cn = self.RegisterClass()
        self.BuildWindow(cn)
        
        rect = win32gui.GetClientRect(self.hwnd)
        win32gui.SetWindowPos(self.hwnd, 0, 0, 0, 400, (500-rect[3])+self.friend_list_len*24, win32con.SWP_NOMOVE|win32con.SWP_NOOWNERZORDER)
        for i in range(len(self.friend_list)):
            if i >= self.friend_list_len:
                break
            name = self.friend_list[i][1]
            ip = self.friend_list[i][0]
            friend_id = self.friend_list[i][3]
            email = self.friend_list[i][4]
            fli = FLI.create(self, ip, name, friend_id, email, 0, 24*i, rect[2], 24)
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
        '''check character and updata if need'''   
        myThread = threading.Thread(target=self.recvVersionAndUpdata)
        myThread.setDaemon(True)
        myThread.start()
        '''check new email'''
#         myThread = threading.Thread(target=self.checkEmail)
#         myThread.setDaemon(True)
#         myThread.start()
        
        point = win32gui.GetCursorPos()

        self.tk_mainloop = tk.Tk()
        self.tk_mainloop.withdraw()
        self.tk_mainloop.mainloop()
        
    def startCheckEmail(self):
        myThread = threading.Thread(target=self.checkEmail)
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
        style = win32con.WS_OVERLAPPEDWINDOW
        w=250
        h=500
            
        self.hwnd = win32gui.CreateWindow(
                             className,
                             "freind list", style,
                             win32con.CW_USEDEFAULT,
                             win32con.CW_USEDEFAULT,
                             w,h,0,0,self.hinst,None)
        self.menubar = win32gui.CreateMenu()
        win32gui.AppendMenu(self.menubar, win32con.MF_STRING, 1, 'search ip')
        win32gui.AppendMenu(self.menubar, win32con.MF_STRING, 2, 'add new friend')
        win32gui.AppendMenu(self.menubar, win32con.MF_STRING, 3, 'log in')
        win32gui.SetMenu(self.hwnd, self.menubar)
    
    def OnSize(self, hwnd, msg, wp, lp):
        '''get client w, h'''
        w, h = win32api.LOWORD(lp), win32api.HIWORD(lp)
        if h != self.friend_list_len*24:
            '''resize the height if needed'''
            winRect = win32gui.GetWindowRect(hwnd)
            winW = winRect[2]-winRect[0]
            winH = (winRect[3]-winRect[1]-h)+self.friend_list_len*24
            win32gui.SetWindowPos(self.hwnd, 0, 0, 0, winW, winH, win32con.SWP_NOMOVE|win32con.SWP_NOOWNERZORDER)
        else:
            for i in range(len(self.friend_list_item_list)):
                list_item = self.friend_list_item_list[i]
                itemH = h//self.friend_list_len
                win32gui.SetWindowPos(list_item.hwnd, 0, 0, i*itemH, w, itemH, win32con.SWP_NOOWNERZORDER)
        return True
        
    def OnCommand(self, hwnd, msg, wp, lp):
        if win32api.HIWORD(wp) == 0: #menu command
            menu_id = win32api.LOWORD(wp)
            if menu_id == 1:
                point = win32gui.GetCursorPos()
                COW.open_check_online_window(point[0], point[1])
            elif menu_id == 2:
                point = win32gui.GetCursorPos()
                OpenAddFriendWindow(point[0], point[1], self)
            elif menu_id == 3:
                OpenLogInWindow(self)
        
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
        print('ocait', sock)
        
    def OnConnAccepted(self, hwnd, msg, wp, lp):
        '''
        win32 callback
        manage the connection stored in self.newconn_queue
        be aware of that the order of connection may not be ordered by time
        '''
        sock, addr = self.newconn_queue.get()
        
        for (ip, name, status, id, email, new_eamil_flag) in self.friend_list:
            if ip == addr[0]:
                self.StartChat(id, sock)
                print('user', name, 'connected at', addr)
                print('chat started, character opened')
                return
        
        mp.sendPacket(sock, b'ok')
        mt.SendChatEndMessage(sock)
        sock.close()
        print('unknown connection from (%s) rejected'%addr[0])
        
    def RefreashFriendStatusInThread(self):
        while True:
            time.sleep(1)
            self.updated_friends = self.friend_list.RefreshOnlineStatus()
            if len(self.updated_friends) > 0:
                win32gui.SendMessage(self.hwnd, WM_FRIENDREFRESHED, 0, 0)
    
    def OnFriendRefreshed(self, hwnd, msg, wp, lp):    
        for index in self.updated_friends:
            print('find friend:', self.friend_list[index][1])
            for item in self.friend_list_item_list:
                friend_id = self.friend_list[index][3]
                if item.IdIsMe(friend_id): 
                    print('friend in list')
                    item.model.online = not item.model.online
                    chat_win = self.GetChatWin(friend_id)
                    if chat_win:
                        chat_win.online = item.model.online
                    if item.model.online:
                        print(self.friend_list[index][1])
                        if chat_win and chat_win.cht_str_msg != '':
                            sock = mt.StartTalking(self.friend_list[index][0])
                            
                            if sock:
                                chat_win.setConnectedSocket(sock, is_connectee=False)
                                
                                self.sendMessageFrom_cht_str_msg(chat_win)
                                #mt.SendChatEndMessage(sock)
                                print('send offline msg')

                    win32gui.InvalidateRect(item.hwnd, (FLI.online_indicate_rect),True)

    def sendMessageFrom_cht_str_msg(self, chat_win):
        if chat_win.cht_str_msg == '':
            return 
        for msg in chat_win.cht_str_msg.split('\n'):
            mt.SendMessageAndAnime(chat_win.conn_socket, msg, '')
            chat_win.this_messages.append(msg)
            chat_win.sended_message_read = False #no need but on logical
            chat_win.showSentChatMsgWin(msg)
        chat_win.cht_str_msg == ''

    def SetFriendNewMail(self, index, new_mail_status, new_mails):
        '''index: index of friendList; mew_mail_status: True of False
            new_mails: new mails list to insert in''' 
        self.friend_list[index][5] = new_mail_status
        #if friend is in friend_list_item_list, refresh it
        if index >= self.friend_first_index and index-self.friend_first_index < self.friend_list_len:
            self.refreshFriendListItem(index-self.friend_first_index)
        self.friend_new_mails[index].extend(new_mails)
        
    def refreshFriendListItem(self, index):
        '''make friend_list_item window show current status
           index: index of friend_list_item windows, not of friendList'''
        item = self.friend_list_item_list[index]
        item.SetFriendData(self.friend_list[index + self.friend_first_index])
        win32gui.InvalidateRect(item.hwnd, None, True)

    def OnMouseWheel(self, hwnd, msg, wp, lp):
        delta = wp>>16
        if delta//win32con.WHEEL_DELTA == 0:
            if delta < 0:
                delta = -1
            elif delta > 0:
                delta = 1
        else:
            delta = delta//win32con.WHEEL_DELTA
        
        self.friend_first_index -= delta
        if self.friend_first_index < 0:
            self.friend_first_index = 0
        elif self.friend_list_len > len(self.friend_list):
            pass
        elif self.friend_first_index + self.friend_list_len > len(self.friend_list):
            self.friend_first_index = len(self.friend_list) - self.friend_list_len
            
        for i in range(self.friend_list_len):
            self.refreshFriendListItem(i)
        return True
    
    def OnDestroy(self, hwnd, msg, wp, lp):
        for each in self.friend_list_item_list:
            try:
                win32gui.DestroyWindow(each.hwnd)
            except:pass
            try:
                each.edit_window.destroy()
            except:pass
        for each in self.chat_wins:
            try:win32gui.DestroyWindow(each.hwnd)
            except:pass
        self.friend_list.Save()
        self.tk_mainloop.destroy()
        self.tk_mainloop.quit()
        win32gui.DestroyMenu(self.menubar)
        win32gui.PostQuitMessage(0)
        return win32gui.DefWindowProc(hwnd, msg, wp, lp)
    
    def getFriendsEmail(self):
        friends = []
        for frined in self.friend_list:
            if frined[4] != '':
                friends.append(frined[4])
        return friends
  
    def checkEmail(self):
        email = mailHandle.Email()
        isChange = True
        strEmail = self.email
        email_passwd = self.email_passwd
        while True:
            if isChange and (email.login(self.email, self.email_passwd)):
                break
            time.sleep(5)
            if (strEmail == self.email) and (email_passwd == self.email_passwd):
                isChange = False
            else:
                strEmail = self.email
                email_passwd = self.email_passwd
                isChange = True
        while True:
            friends = self.getFriendsEmail()
            email.setFriends(friends)
            mailDict = email.getEmail()
            if mailDict == None:
                time.sleep(60)
                myThread = threading.Thread(target=self.checkEmail)
                myThread.setDaemon(True)
                myThread.start()
                return
            for key in mailDict.keys():
                for index in range(len(self.friend_list)):
                    friend = self.friend_list[index]
                    if friend[4] == key:
                        print(key)                     
                        self.SetFriendNewMail(index, True, mailDict[key])
                        break
            time.sleep(60)
     
    
    def recvVersionAndUpdata(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 12348))
        sock.listen(2)
        while True:
            sc, scName= sock.accept()
            print('update requested')
            friendID = None
            myChafile = None
            callbackfunc = None
            print(scName[0])
            friend_found = False
            time.sleep(1)
            for each in self.chat_wins:
                if each.ip == scName[0]:
                    while True:#wait until window created
                        try:
                            friendID = each.friendID
                            myChafile = each.myCharFile
                            callbackfunc = each.setChadisplay
                            break
                        except: 
                            time.sleep(0.1)
                    friend_found = True
                    break
            if friend_found:
                arg = (sc, myChafile, friendID, callbackfunc)
                threading.Thread(None, updataIfNeed, args=arg).start()
            else:
                sc.close()
    
    def GetChatWin(self, friend_id):
        for win in self.chat_wins:
            if win.friendID == friend_id:
                return win
        return None
    
    def getCharPath(self, user_id, character_id):
        return 'data/'+user_id+'/char/'+character_id+'/character1.txt'
    
    def StartChat(self, friend_id, sock=None):
        '''
        Create a image_window here
        should be the only entrance of image_window
        give a new socket to chat_win if chat_win is windowed
        '''
        chat_win = self.GetChatWin(friend_id)
        if chat_win != None and win32gui.IsWindow(chat_win.hwnd):
            if sock == None:
                raise Exception('start chat when opened, without socket')
            else:
                chat_win.setConnectedSocket(sock)
                chat_win.online = True
                return
        
        for i in range(len(self.friend_list)):
            friend=self.friend_list[i]
            ip = friend[0]
            name = friend[1]
            id = friend[3]
            if id == friend_id:
                win = image_window(
                    self.OnChatClosed, 
                    name, 
                    sock, 
                    ip, 
                    self.getCharPath(id, self.char_id),
                    id)
                
                list_item_index = i-self.friend_first_index 
                if list_item_index >= 0 and list_item_index < self.friend_list_len:
                    self.friend_list_item_list[list_item_index].SetFriendData(friend)
                # set if friend online
                win.online = friend[2]
                self.chat_wins.append(win)
                break
        
        print('character created')
        '''tricky!HACK! stuck here'''
    
    def OnChatClosed(self, chat_win):
        '''hand made callback, passed to image_window
        called after image_window closed
        ensure you know what you're doing'''
        '''set button text 'chat' '''
        for item in self.friend_list_item_list:
            if item.model.friend_id == chat_win.friendID:
                item.OnChatClosed()
                
        self.sendOfflineMessage(chat_win)
        
        self.chat_wins.remove(chat_win)
        
    def sendOfflineMessage(self, chat_win):
        strContent = chat_win.cht_str_msg
        if strContent == '':
            return True
        recipient = ''
        for index in range(len(self.friend_list)):
            friend = self.friend_list[index]
            if friend[1] == chat_win.chat_name:
                recipient = friend[4]
                break
        if recipient == '':
            return False
        strSubject = 'Message from ' + chat_win.chat_name

        email = mailHandle.Email()
        if email.login(self.email, self.email_passwd):
            if email.sendMailSmtp(recipient, strSubject, strContent):
                return True
        return False
    
    def IncreaseFriendListItemWhenAddNewFriendIfLessThanDefault(self):
        rect = win32gui.GetClientRect(self.hwnd)
        name = self.friend_list[len(self.friend_list_item_list)][1]
        ip = self.friend_list[len(self.friend_list_item_list)][0]
        friend_id = self.friend_list[len(self.friend_list_item_list)][3]
        email = self.friend_list[len(self.friend_list_item_list)][4]
        if (len(self.friend_list_item_list)<4):
            fli = FLI.create(self, ip, name, friend_id, email, 0, 24*len(self.friend_list_item_list), rect[2], 24)
            self.friend_list_item_list.append(fli)
        
        
class OpenAddFriendWindow:
    def __init__(self, x, y, parent_obeject):
        '''
        create the add friend window.
        '''
        self.parent = parent_obeject
        self.root = tk.Tk()
        self.root.title('add new friend')
        self.input_panes = tk.PanedWindow(self.root,orient=tk.HORIZONTAL)
        self.input_panes.pack(fill=BOTH, expand=1)
        self.lable_for_ip = tk.Label(self.input_panes, text='ip:')
        self.entry_for_ip = tk.Entry(self.input_panes, width=10)
        self.lable_for_name = tk.Label(self.input_panes, text='name:')
        self.entry_for_name = tk.Entry(self.input_panes, width=10)
        self.lable_for_eamil = tk.Label(self.input_panes, text='email:')
        self.entry_for_eamil = tk.Entry(self.input_panes, width=15)
        self.input_panes.add(self.lable_for_ip)
        self.input_panes.add(self.entry_for_ip)
        self.input_panes.add(self.lable_for_name)
        self.input_panes.add(self.entry_for_name)
        self.input_panes.add(self.lable_for_eamil)
        self.input_panes.add(self.entry_for_eamil)
        self.button_panes = tk.PanedWindow(self.root,orient=tk.HORIZONTAL, width=15)
        self.button_panes.pack(fill=BOTH, expand=1)
        self.button_for_add = tk.Button(self.button_panes, text="Add this friend", command=self.CommitEntry)
        self.button_for_close = tk.Button(self.button_panes, text="Exit", command=self.Destroy, width=5)
        self.button_panes.add(self.button_for_close) 
        self.button_panes.add(self.button_for_add)
        self.root.geometry('+%d+%d'% (x,y))
        
    def CommitEntry(self):
        ip = self.entry_for_ip.get()
        name = self.entry_for_name.get()
        email = self.entry_for_eamil.get()
        self.parent.friend_list.AddNewFriend(ip, name, email) 
        self.parent.IncreaseFriendListItemWhenAddNewFriendIfLessThanDefault()
        
    def Destroy(self):
        self.root.destroy()
        
class OpenLogInWindow:
    '''
    You should reload account/password after use this class
    '''
    def __init__(self, friendwin=None):
        self.friendwin = friendwin
        self.root=tk.Tk()
        self.root.title('Enter account/passwarod to log in')
        self.account_panew=tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.password_panew=tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.button_panew=tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.account_panew.pack(fill=BOTH)
        self.password_panew.pack(fill=BOTH)
        self.button_panew.pack(fill=BOTH)
        self.account_label=tk.Label(self.account_panew, text='Account: ')
        self.account_entry=tk.Entry(self.account_panew, width=10)
        self.password_label=tk.Label(self.password_panew, text="password: ")
        self.password_entry=tk.Entry(self.password_panew, width=10, show="*")
        self.account_panew.add(self.account_label)
        self.account_panew.add(self.account_entry)
        self.password_panew.add(self.password_label)
        self.password_panew.add(self.password_entry)
        self.login_btn=tk.Button(self.button_panew, text='Login', command=self.login)
        self.close_btn=tk.Button(self.button_panew, text='Close', command=self.Destory)
        self.button_panew.add(self.login_btn)
        self.button_panew.add(self.close_btn)

        try:
            with open('acpwd.txt') as file:
                for line in file:
                    acpwd = line.split(':')
                    self.account_entry.insert(0, acpwd[0])
                    self.password_entry.insert(0, acpwd[1])
        except:
            pass

        
    def login(self):
        account=self.account_entry.get()
        password=self.password_entry.get()
        myEmail = mh.Email(account, password)
        success = myEmail.login()
        if success==True:
            with open('acpwd.txt', 'w') as file:
                file.write(account+':'+password)
            self.Destory()
            self.friendwin.startCheckEmail()
            
            
        else:
            self.account_entry.delete(0, tk.END)
            self.account_entry.insert(0, 'Login Failed!')
        
    def Destory(self):
        self.root.destroy()
        
    '''   
    def checkEmail(self):
        email = mailHandle.Email()
        isChange = True
        strEmail = self.email
        email_passwd = self.email_passwd
        while True:
            if isChange and (email.login(self.email, self.email_passwd)):
                break
            time.sleep(5)
            if (strEmail == self.email) and (email_passwd == self.email_passwd):
                isChange = False
            else:
                strEmail = self.email
                email_passwd = self.email_passwd
                isChange = True
        while True:
            friends = self.getFriendsEmail()
            email.setFriends(friends)
            mailDict = email.getEmail()
            if mailDict == None:
                time.sleep(60)
                myThread = threading.Thread(target=self.checkEmail)
                myThread.setDaemon(True)
                myThread.start()
                return
            for key in mailDict.keys():
                for index in range(len(self.friend_list)):
                    friend = self.friend_list[index]
                    if friend[4] == key:
                        print(key)                     
                        self.SetFriendNewMail(index, True, mailDict[key])
                        break
            time.sleep(60)    
            
    def getFriendsEmail(self):
        friends = []
        for frined in self.friend_list:
            if frined[4] != '':
                friends.append(frined[4])
        return friends
    '''
        
import time
if __name__ == '__main__':
    mainwin = FriendWin()
    
    '''play as a remote user to test recving functions'''
    # end win32 windows
    win32gui.PumpMessages()
    print('end')
