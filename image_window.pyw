# example1.py
import os
from synchronizationRole import updataIfNeed
import zipfile
import struct
import win32api
import win32con
import win32gui
import threading
import Image
import time
import socket
import online_check as oc
import tkinter as tk
import message_transaction as mt
import tkinter.messagebox as tkmb
from WM_APP_MESSAGES import *
from win32api import RGB
import queue
from tkinter import Entry
import myPacket as mp
import elfAutoBehavior
import mailHandle
from winsound import PlaySound, SND_ASYNC
from random import randint
config_file="config"
history_file="history"
#execute once
className = "image_window"
wc = win32gui.WNDCLASS()
wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
wc.lpfnWndProc = win32gui.DefWindowProc
wc.cbWndExtra = 0
wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
wc.hbrBackground = win32con.COLOR_WINDOW + 1
wc.hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
wc.lpszClassName = className
wc.cbWndExtra = win32con.DLGWINDOWEXTRA +struct.calcsize("Pi")
# wc.hIconSm = 0
win32gui.RegisterClass(wc)

def getXY(lparam):
    return lparam&0xffff, (lparam>>16)&0xffff

def turnOffTk(tk_object):
    tk_object.destroy()

'''def getCharacter(fileName):
    charFile = open(fileName, 'r')
    charData=[]
    for line in charFile.readlines():       
        charData.append(line.split())
    charFile.close()
    return charData'''
def getCharacter(fileName):
    charFile = open(fileName, 'r')
    charData=[]
    for line in charFile.readlines():     
        temp = line.split()
        temp[0] = os.path.abspath(os.path.join(fileName, os.pardir))+'/'+temp[0]  
        charData.append(temp)
    charFile.close()
    return charData
class image_window:
    '''
    modify .message_map to handle messages
    init is the constructor
    stuck in run() and released after closed
    SetImages() to set a list of paths
    SwitchNextImage() let you switch to next image
    TODO 
    sending message
    allowing multiline message
    preview anime
    '''
    def __init__(self, after_window_close, friend_name, sock, ip, characterFile, id):
        '''
        sock maybe None, indicates the window is not connected currently.
        '''
        win32gui.InitCommonControls()
        self.hinst = win32api.GetModuleHandle(None)
        '''for show action easy to draw'''
        self.image_index = 0
        '''for show action easy to draw'''
        self.friendID = id
        self.Image_list = []
        self.message_map = {
          win32con.WM_DESTROY: self.OnDestroy,
          win32con.WM_LBUTTONDOWN: self.OnLButtonDown,
          win32con.WM_LBUTTONUP: self.OnLButtonUp,
          win32con.WM_MOVE: self.OnMove,
          win32con.WM_SIZE:self.OnSize,
          win32con.WM_MOUSEMOVE: self.OnMouseMove,
          win32con.WM_PAINT: self.OnPaint,
          win32con.WM_RBUTTONUP: self.OnRButtonUp,
          WM_CHATMSGRECV: self.OnChatMessageReceived,
        }
        '''create the window '''
        self.BuildWindow("image_window")
        '''set the message mapping '''
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_WNDPROC, self.message_map)
        '''read the configurations from file'''
        try:
            self.readCheck=False
            self.autoBehave = False
            self.myCharFile = 'data/character1/character1.txt'
            self.ReadConfig()
        except Exception: 
            print('no config file')  
        
        '''whether chatter is online'''
        self.online = False
        '''whether the drag action is showing'''
        self.drag_showing = False
        '''whether character is being dragged''' 
        self.dragging = False
        '''history'''
        self.this_messages=[]
        '''for display'''
        self.chat_name = friend_name
        ''''speak window'''
        self.speak_window = None
        '''speak window'''
        self.speak_window_hwnd = 0
        '''name window'''
        self.name_win = None
        self.ShowNameWin()
        self.history_window_width = 30 # in character
        '''callback function to be execute in ondestroy'''
        self.after = after_window_close
        '''for socket connection'''
        self.ip = ip
        '''the socket , whether connected or not'''
        self.conn_socket = None
        '''the character file (path of bitmaps)'''
        self.charFile = characterFile
        '''the chat msg queue for thread to insert into
           and for main thread to get from'''
        self.chatmsg_queue = queue.Queue()
        '''the chat msg window showing'''
        self.chat_msg_win = []
        '''offline Message string'''
        self.cht_str_msg = ''
        '''the sent msg window showing'''
        self.sent_msg_win = None
        print('the path input image_window get: ',self.getActionPath('idle.txt'))
        self.showAction(self.getActionPath('idle.txt'), True)
        '''for read cheack'''
        
        self.actionNow = None
        actionList = self.getAutoBehaviorActions()
        self.elfAutoBehaviorThread = elfAutoBehavior.ElfAutoBehavior(self, actionList)
        self.elfAutoBehaviorThread.setDaemon(True)
        self.elfAutoBehaviorThread.start()
        
        self.receive_message_read = True #no not yet read received message
        self.sended_message_read = True #he/she already read message
        
        if sock != None:
            self.setConnectedSocket(sock)
        '''for selecting the anime to send'''
        self.tmp_anime=""      
    
    def getAutoBehaviorActions(self):
        path = self.getParentDirectory(self.charFile) + '/skeleton/'
        anime_list = [f for f in os.listdir(path) if os.path.splitext(f)[1]=='.txt']
        with open(path+'autoBehave.config') as file:
            accept_list = [line[:-1] for line in file] 
        result_list = ['walk.txt']
        for anime in anime_list:
            if accept_list.count(anime) > 0:
                result_list.append(anime)
                
        return result_list
    
    def setConnectedSocket(self, sock, is_connectee=True):
        print('set connected socket', sock.getpeername())
        if self.conn_socket != None:
            try:
                mt.SendChatEndMessage(self.conn_socket)
            except:pass
            self.conn_socket.close()
            self.conn_socket = sock
#             raise Exception('set socket when connected')
        self.conn_socket = sock
        if is_connectee:
            mp.sendPacket(self.conn_socket, b'ok')
        else:
            assert mp.recvPacket(self.conn_socket) == b'ok'
        self.DoAfterConnectEstablished()
    
    def DoAfterConnectEstablished(self):
        thread = threading.Thread(target=self.listen_to_chat_messagesInThread)
        thread.setDaemon(True)
        thread.start()
        
    def ReadConfig(self):
        with open(config_file) as file:
            for line in file:
                if line[-1] == '\n':
                    line = line[:-1]
                cap = line.split(":")
                if cap[0] == 'readCheck':
                    self.readCheck=bool(cap[1]=='True')
                elif cap[0] == 'myCharFile':
                    self.myCharFile = cap[1]
                elif cap[0] == 'autoBehave':
                    self.autoBehave = (cap[1]=='True')
                
    def BuildWindow(self, className):
        style = win32con.WS_POPUP|win32con.WS_VISIBLE
        xstyle = win32con.WS_EX_LAYERED
        
        self.hwnd = win32gui.CreateWindowEx(
                             xstyle,
                             className,
                             "image_window",
                             style,
                             randint(200,800),
                             randint(200,500),
                             130,
                             130,
                             0,
                             0,
                             self.hinst,
                             None)
        win32gui.SetLayeredWindowAttributes(self.hwnd, RGB(255,255,255),0,win32con.LWA_COLORKEY)
        self.StayTop()
        
    def SetImages(self, Image_list):
        '''private purpose, for showing action implementation'''
        try:
            for image in self.Image_list:
                image.release_img()
        except:pass
        self.Image_list = Image_list
        self.image_index = -1
    
    def SwitchNextImage(self):
        '''private purpose, for showing action implementation
           maybe call Resize here'''
        self.image_index = (self.image_index+1)%len(self.Image_list)
        
        #redrawing
        win32gui.InvalidateRect(self.hwnd, None, True)
    
    def GetCurrentImageRemainTime(self):
        return self.image_remain_times[self.image_index]
    def MoveTo(self, x, y):
        win32gui.SetWindowPos(self.hwnd, 0, x, y, 0, 0, win32con.SWP_NOSIZE|win32con.SWP_NOOWNERZORDER)
    def GoOnTop(self):
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOMOVE|win32con.SWP_NOSIZE)
    def StayTop(self):
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE|win32con.SWP_NOSIZE)
    def Resize(self, w, h):
        win32gui.SetWindowPos(self.hwnd, 0, 0, 0, w, h, win32con.SWP_NOMOVE|win32con.SWP_NOOWNERZORDER)
    
    def OnNCCreate(self, hwnd, message, wparam, lparam):
        '''
        DO NOT edit unless you know what you're doing
        '''
        return True
    
    def OnLButtonDown(self, hwnd, message, wparam, lparam):
        self.dragging = True
        self.drag_point = win32gui.ClientToScreen(self.hwnd, (win32api.LOWORD(lparam), win32api.HIWORD(lparam)))
        self.drag_pre_pos =  win32gui.ClientToScreen(self.hwnd, (0,0))
        win32gui.SetCapture(hwnd)
        return True
    
    def OnLButtonUp(self, hwnd, message, wparam, lparam):
        '''2.Click on image_window so send i read the message'''
        if self.receive_message_read == False: #if there are messages not read, now is reading
            if self.readCheck == True:
                mt.SendMessageAndAnime(self.conn_socket, '', 'checked') # tell I read it
            self.receive_message_read=True #no message not read
            self.DestroyChatMsgWins()
        
        if self.drag_showing == False:
            self.showAction(self.getActionPath('click.txt'))
        else:
            self.showAction(self.getActionPath('idle.txt'))
        self.dragging = False
        self.drag_showing = False
        win32gui.ReleaseCapture()
        '''set other attaced windows' position, if put this in OnMove(), cause vanishing'''
        self.SetAttachedWinPos()
        return True
    
    def OnMouseMove(self, hwnd, message, wparam, lparam):
        if self.dragging :
            cur_x, cur_y = win32gui.ClientToScreen(self.hwnd, (win32api.LOWORD(lparam), win32api.HIWORD(lparam)))
            '''deal for negative cur_x, cur_y'''
            if cur_x > (1<<15)-1:
                cur_x -= (1<<16)
            if cur_y > (1<<15)-1:
                cur_y -= (1<<16)
            dx = cur_x-self.drag_point[0]
            dy = cur_y-self.drag_point[1]
            if abs(dx)+abs(dy) < 1:
                return True
            self.drag_point = (cur_x, cur_y)
            if not self.drag_showing:
                self.drag_showing = True
                self.showAction(self.getActionPath('drag.txt'), True)
            rect = win32gui.GetWindowRect(self.hwnd)
            x, y = rect[0], rect[1]
            
            self.MoveTo(x+dx, y+dy)
            
        return True
    def OnRButtonUp(self, hwnd, message, wparam, lparam):
        menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(menu, win32con.MF_STRING, 1, 'speak')
        win32gui.AppendMenu(menu, win32con.MF_STRING, 2, 'read check')
        win32gui.AppendMenu(menu, win32con.MF_STRING, 3, 'historical messages')
        win32gui.AppendMenu(menu, win32con.MF_STRING, 5, 'auto behave')
        win32gui.AppendMenu(menu, win32con.MF_STRING, 4, 'close')
        if self.readCheck == True: #check new menu's mark
            win32gui.CheckMenuItem(menu, 2, win32con.MF_CHECKED)
        if self.autoBehave == True:
            win32gui.CheckMenuItem(menu, 5, win32con.MF_CHECKED)
        x, y = getXY(lparam)
        x, y = win32gui.ClientToScreen(hwnd, (x, y))
        '''show the popup menu, 0x100 means return item id right after'''
        item_id = win32gui.TrackPopupMenu(menu, 0x100, x, y, 0, hwnd, None)
        if item_id == 1:
            try:
                turnOffTk(self.speak_window)
                self.speak_window = None
                self.speak_window_hwnd = 0
            except Exception:
                self.ShowSpeakWindow()
        elif item_id == 2:
            self.readCheck=not self.readCheck
        elif item_id == 3:
            try:
                turnOffTk(self.history_window)
                self.history_window = None
            except Exception:
                self.ShowHistoryWindow()
        elif item_id == 4:
            win32gui.DestroyWindow(self.hwnd)
        elif item_id == 5:
            self.autoBehave = not self.autoBehave    
        
        win32gui.DestroyMenu(menu)
        return True
    
    def OnMove(self, hwnd, message, wparam, lparam):
        '''
        called when window is moved.
        control things here
        '''
        if not self.dragging:
            self.SetAttachedWinPos()
        return win32gui.DefWindowProc(hwnd, message, wparam, lparam)
    
    def OnSize(self, hwnd, message, wparam, lparam):
        '''
        called when window is resized.
        control things here
        '''
        self.SetAttachedWinPos()
        return win32gui.DefWindowProc(hwnd, message, wparam, lparam)
    
    def SetAttachedWinPos(self):
        try:self.speak_window.geometry('+%d+%d' % self.GetSpeakWindowPos())
        except :pass
        for i in range(len(self.chat_msg_win)):
            try:self.chat_msg_win[i].geometry('%dx%d+%d+%d' % self.GetChatMsgWinSizePos(i))
            except :pass
        try:self.sent_msg_win.geometry('%dx%d+%d+%d' % self.GetSentMsgWinSizePos())
        except :pass
        try:
            self.name_win.geometry('+%d+%d'%self.GetNameWinPos())
        except :pass
         
    def GetNameWinPos(self):
        '''control the position of speaking window'''
        x = (win32gui.GetWindowRect(self.hwnd)[0]+win32gui.GetWindowRect(self.hwnd)[2])//2\
            - len(self.chat_name)*5
        y = win32gui.GetWindowRect(self.hwnd)[3]
        if self.speak_window != None:
            y += 50
        return x,y

    def GetSpeakWindowPos(self):
        '''control the position of speaking window'''
        x = win32gui.GetWindowRect(self.hwnd)[0]
        y = win32gui.GetWindowRect(self.hwnd)[3]
        return x,y
    
    def ShowSpeakWindow(self):
        '''
        show the speaking window.
        this function does not close it even if it's shown.
        '''
        self.speak_window = tk.Tk()
        self.speak_window.overrideredirect(True)
        self.speak_window.wm_attributes('-alpha',1,'-disabled',False,'-toolwindow',True, '-topmost', True)
        frame = tk.Frame(self.speak_window)
        self.input_text = tk.Entry(frame)
        self.input_text.pack(side='left',expand=True, fill='both')
        self.input_text.bind('<Return>', func=self.InputTextHitReturn)
        send_btn = tk.Button(frame, text='send', command=self.SendText)
        send_btn.pack(side='right')
        anime_btn = tk.Button(frame, text='anime', command=self.SelectAnime)
        anime_btn.pack(side='right')
        frame.pack()
        
        self.input_text.focus()
        self.speak_window.geometry('+%d+%d' % self.GetSpeakWindowPos())
        self.speak_window_hwnd = win32gui.GetForegroundWindow()
        win32gui.SetFocus(self.speak_window_hwnd)
        self.SetAttachedWinPos()
    
    def ShowNameWin(self):
        '''show msg in a new bubble window'''
        r = tk.Toplevel()
        r.overrideredirect(True)
        f = tk.Frame(r, bd=1,bg='black')
        var = tk.StringVar()
        l = tk.Label(f,bg='#bbffdd', justify='center', fg='black', font=('Consolas', 17),textvariable=var)
        var.set(self.chat_name)
        l.pack(fill='both',expand=True)
        f.pack(fill='both',expand=True)
        r.wm_attributes('-toolwindow',True, '-topmost', True)
        r.geometry('+%d+%d'%self.GetNameWinPos())
        self.name_win = r
        
    def ShowNewChatMsgWin(self, msg):
        '''show msg in a new bubble window'''
        r = tk.Toplevel()
        r.overrideredirect(True)
        f = tk.Frame(r, bd=1,bg='black')
        var = tk.StringVar()
        l = tk.Label(f,bg='#bbddff', justify='center', fg='black', textvariable=var)
        var.set(msg)
        l.pack(fill='both',expand=True)
        f.pack(fill='both',expand=True)
        r.wm_attributes('-toolwindow',True, '-topmost', True)
        #r.geometry('%dx%d+%d+%d'%self.GetNewChatMsgWinSizePos())
        self.chat_msg_win.append(r)
        self.SetAttachedWinPos()
    
    def showSentChatMsgWin(self, msg):
        r = tk.Toplevel()
        r.overrideredirect(True)
        f = tk.Frame(r, bd=1,bg='black')
        var = tk.StringVar()
        l = tk.Label(f,bg='#bbddff', justify='center', fg='black', textvariable=var)
        var.set(msg)
        l.pack(fill='both',expand=True)
        f.pack(fill='both',expand=True)
        r.wm_attributes('-toolwindow',True, '-topmost', True)
        r.geometry('%dx%d+%d+%d'%self.GetSentMsgWinSizePos())
        try:
            self.sent_msg_win.destroy()
        except:pass
        self.sent_msg_win = r
        
    def InputTextHitReturn(self, event):
        self.SendText()
        
    def GetChatMsgWinSizePos(self, index):
        '''control the position of new chat msg'''
        w = 200
        h = 32
        y_dis = 7
        x = win32gui.GetWindowRect(self.hwnd)[0]
        y = win32gui.GetWindowRect(self.hwnd)[1] - (y_dis+h)*(len(self.chat_msg_win) - index)
        return w,h,x,y
    
    def GetSentMsgWinSizePos(self):
        w = 250
        h = 32
        y_dis = 7
        x_dis = 10
        rect = win32gui.GetWindowRect(self.hwnd) 
        x = rect[2] + x_dis
        y = (rect[3]+rect[1])//2
        return w,h,x,y
    
    def GetNewChatMsgWinSizePos(self):
        return self.GetChatMsgWinSizePos(len(self.chat_msg_win))
        
    def GetHistoryWindowPos(self):
        '''control the position of history window'''
        return win32gui.GetCursorPos()
    
    def GetHistoryString(self):
        '''
        read history file and make it pretty
        return a pretty string for history window display
        '''
        s = ''
        try:
            with open('data/'+str(self.friendID)+'/'+history_file) as file:
                for line in file.read().splitlines():
                    s += line+'\n'
        except Exception:pass
        for i in range(self.history_window_width):
            s += '-'
        s += '\n'
        for msg in self.this_messages:
            s += msg+'\n'
        return s
    
    def ShowHistoryWindow(self):
        '''
        set self.history_window a tk loop
        '''
        '''the window'''
        self.history_window = tk.Tk()
        self.history_window.wm_attributes('-toolwindow',True)
        self.history_window.resizable(width=False, height=False)
        self.history_window.title('[%s] %s' % ('HISTORY', self.chat_name))
        '''the history text'''
        text = tk.Text(self.history_window,
                       exportselection=0,
                       width=self.history_window_width,
                       height=10)
        text.insert(tk.END, self.GetHistoryString())
        text.config(state=tk.DISABLED)
        text.pack(side='left',fill='y')
        '''create scrollbar'''
        scrollbar = tk.Scrollbar(self.history_window)
        scrollbar.pack(side='right', fill='y')
        '''enable scrolling'''
        text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text.yview)
        '''set position and size, and then show it'''
        self.history_window.geometry('+%d+%d' % self.GetHistoryWindowPos())
        
    def SelectAnime(self):
        '''
        show anime list for user to choose, or hide it if it was shown.
        TODO: change name to OnSelectShowAnime.
        '''
        if hasattr(self, 'anime_lb') and self.anime_lb != None :
            self.anime_lb.destroy()
            self.anime_lb = None
            self.tmp_anime = ''
        else:
            anime_list = self.getSelfActionList()
            self.anime_lb = tk.Listbox(self.speak_window, height = len(anime_list))
            self.anime_lb.bind("<<ListboxSelect>>", self.OnSelect)
            for i in range(len(anime_list)):
                self.anime_lb.insert(i+1, anime_list[i])
            self.anime_lb.pack(expand=True, fill='both')
        
    def OnSelect(self, event):
        widget = event.widget
        selection=widget.curselection()
        value = widget.get(selection[0])
        self.tmp_anime = value
        
    def set_cht_str_msg(self):
        msg = self.input_text.get()
        self.input_text.delete(0, tk.END)
        self.cht_str_msg += msg + '\n'
        
    def SendText(self):
        '''
        SendText to remote chatter
        '''
        '''get the speak_window handle'''
        self.speak_window_hwnd = win32gui.GetForegroundWindow()
        if self.conn_socket == None:
            if self.online == True:
                print('try connect to', self.ip)
                self.conn_socket = mt.StartTalking(self.ip)
                print('result:', self.conn_socket)
            if self.conn_socket == None:
                self.set_cht_str_msg()
                return 
            
            myThread = threading.Thread(target=self.sendVersionAndUpdata)
            myThread.setDaemon(True)
            myThread.start()
            assert mp.recvPacket(self.conn_socket) == b'ok'
            self.DoAfterConnectEstablished() 
        
        msg = self.input_text.get()
        msg = msg.replace('\n', '')
        msg = msg.replace('\r', '')

        mt.SendMessageAndAnime(self.conn_socket, msg, self.tmp_anime)

        self.this_messages.append('you: '+msg)
        '''1.send new message so readCheck set to False'''
        self.sended_message_read = False #no need but on logical
        if msg != '':
            self.showSentChatMsgWin(msg)
        
        self.showAction(self.getActionPath('send.txt'))
        self.input_text.delete(0, tk.END)
        win32gui.SetFocus(self.speak_window_hwnd)
        
    def OnPaint(self, hwnd, message, wparam, lparam):
        dc,ps = win32gui.BeginPaint(hwnd)
        if len(self.Image_list)>0:
            self.Image_list[self.image_index].draw_on_dc(dc, RGB(255,255,255))
        win32gui.EndPaint(hwnd, ps)
        return True
    
    def DestroyChatMsgWins(self):
        for win in self.chat_msg_win:
            try:turnOffTk(win)
            except :pass
        self.chat_msg_win = []
    
    def OnDestroy(self, hwnd, message, wparam, lparam):
        '''
        clean things here
        kill all tk things here
        '''
        self.elfAutoBehaviorThread.stop = True
        with open(config_file, 'w') as file:
            file.write('readCheck:'+str(self.readCheck)+'\n')
            file.write('myCharFile:'+str(self.myCharFile)+'\n')
            file.write('autoBehave:'+str(self.autoBehave)+'\n')
        with open('data/'+str(self.friendID)+'/'+history_file, 'a') as file:
            for each in self.this_messages:
                file.write(each+'\n')
        
        try:turnOffTk(self.speak_window)
        except :pass
        try:turnOffTk(self.history_window)
        except :pass
        self.DestroyChatMsgWins()
        try:turnOffTk(self.sent_msg_win)
        except:pass
        try:turnOffTk(self.name_win)
        except:pass
        if self.conn_socket != None:
            mt.SendChatEndMessage(self.conn_socket)
            self.conn_socket.close()
            self.conn_socket = None
        self.after(self)
        return True
    
    def getFileFromPath(self, path):
        names=[]
        temp = path.split('\\')
        for i in temp:
            names += i.split('/')
        return names[len(names)-1]
    
    def getCharFile(self):
        return self.charFile
    def showAction(self, skelFile, repeating = False, acting=True):
        '''
        show an action
        the acting parameter should not be used by public user.
        '''
        skelData=[]
        charFile = open(skelFile, 'r')   
        for line in charFile.readlines():
            skelData.append(line.split())
        charFile.close()    
        
        self.image_remain_times = []
        with open(skelFile+'.config') as file:
            x_size, y_size = [int(v) for v in file.readline().split()]
            for line in file:
                self.image_remain_times.append(float(line))
        
        charData = getCharacter(self.getCharFile())
        self.Resize(x_size, y_size)
        
        charData = sorted(charData,key= lambda temp:int(temp[2]))
        img=[]
        skelTypes = 7
        for i in range(int(len(skelData)/skelTypes)):
            imgTemp = Image.Image()
            temp = skelData[i*skelTypes]
            charDataChange=[]
            if int(temp[5]) != 0:
                for skin in charData:
                    temp = skelData[i*skelTypes + int(skin[1])-1]
                    skin[2] = temp[5]
                    charDataChange.append(skin)
                charDataChange = sorted(charDataChange,key= lambda temp:int(temp[2]))
            else:
                charDataChange = charData
            
            for skin in charDataChange:
                temp = skelData[i*skelTypes + int(skin[1])-1] 
                skinTemp = skin[0]
                if int(temp[4]) != 0:
                    skinTemp, st= skinTemp.split('.', 1)
                    skinTemp = skinTemp + '_' + temp[4] + '.bmp'
                hbmp2 = win32gui.LoadImage(0, skinTemp, win32gui.IMAGE_BITMAP, 0, 0,win32gui.LR_LOADFROMFILE)
                imgTemp.append_component(hbmp2, int(temp[0]), int(temp[1]), int(temp[2]), int(temp[3]))
            img.append(imgTemp)
        self.SetImages(img)
        self.actionNow = self.getFileFromPath(skelFile)
        if acting:
            self.actionThread = ChangeImageThread(self, repeating)
            self.actionThread.setDaemon(True)
            self.actionThread.start()
        else:
            self.actionThread = None
    def showCharacter(self, skelFile):
        '''
        show a animation with only one action
        '''
        self.showAction(skelFile, False)
    
    def listen_to_chat_messagesInThread(self):
        '''
        pre porcess messages in this function
        maybe unpack your message here 
        (if it was packed to ensure the completeness) 
        '''
        print('begin  recving')
        
        while True:
            try:
                msg, anime = mt.RecvMessageAndAnime(self.conn_socket)
                if mt.IsChatEndMessage(msg, anime):
                    '''rcev chat close request, maybe show some anime here'''
                    raise Exception('chat closed by remote')
                elif msg == "" and anime == "checked":  #receive a readCheck
                    '''3.if receive a readCheck confirm'''
                    self.sended_message_read = True #no need but on logical
                    self.showAction(self.getActionPath('read2.txt')) #show message read animation
                    self.sent_msg_win.destroy()
                    continue
                else: self.receive_message_read = False #received a normal message but not readCheck, control to send when next click
            except Exception as e:
                '''chat closed'''
                print(e)
                print('not connected anymore')
                if self.conn_socket  != None:
                    print('close chat')
                    self.conn_socket.close()
                else:
                    print('chat closed before close')
                self.conn_socket = None
                return
            '''send the message to next stage .Control the timing here'''
            self.chatmsg_queue.put((msg, anime))
            win32gui.SendMessage(self.hwnd, WM_CHATMSGRECV, 0, 0)
    
    def OnChatMessageReceived(self, hwnd, win32msg, wp, lp):
        '''
        Called when recv msg
        it's in the main thread, so dealing with gui is safe.
        
        maybe add history here
        '''
        msg, anime = self.chatmsg_queue.get()
        print(msg)
        self.this_messages.append(self.chat_name+': '+msg)
        if msg != '':
            self.ShowNewChatMsgWin(msg) 
            PlaySound('skin/newmessage.wav', SND_ASYNC)
        if anime != '':
            self.showAction(self.getActionPath(anime), repeating= True)
        if self.speak_window_hwnd != 0:
            win32gui.SetFocus(self.speak_window_hwnd)

    def getParentDirectory(self, path):
        #return os.path.abspath(os.path.join(path, os.pardir))
        path2 = path.split('/')
        temp=''
        for ph in path2:
            if(len(ph)>4 and (ph[len(ph)-4:] == '.txt')):
                break
            temp = os.path.join(temp, ph)        
        return temp
    '''          
    def cmpCharVersion(self, myDataSize = 0, hisDataSize = 0):
        if myDataSize == hisDataSize:
            return True
        return False
    
    def getCharDataSize(self, charDirectory):
        temp = 0
        for dirPath, dirNames, fileNames in os.walk(charDirectory):
            for fileName in fileNames:
                file = os.path.join(dirPath, fileName)
                temp += os.path.getsize(file)
        return temp
    
    def checkCharVersion(self):
        text = str(self.getCharDataSize(self.getParentDirectory(self.myCharFile)))
        mp. (self.conn_socket, text.encode('utf8'))
        data = mp.recvPacket(self.conn_socket).decode('utf8')
        if self.cmpCharVersion(self.getCharDataSize(self.getParentDirectory(self.charFile)), int(data)):
            return True
        return False
    
    def updateCharacter(self):
        #fileName = mp.recvPacket(self.conn_socket).decode('utf8')
        fileName = self.friendID+'.zip'
        with open(fileName, 'wb') as cfile:
            while True:
                data = mp.recvPacket(self.conn_socket)
                if data == b'EOF':
                    break
                cfile.write(data)

        win32gui.ShowWindow(self.hwnd, 0)
        os.system('rd /S /Q ' + self.getParentDirectory(self.charFile))
        zf = zipfile.ZipFile(fileName)
        zf.extractall(self.getParentDirectory(self.charFile))
        zf.close()
        win32gui.ShowWindow(self.hwnd, 1)
        os.remove(fileName)
        
    def uploadCharacter(self):
        sfileName = 'ArchiveName.zip'
        zf = zipfile.ZipFile(sfileName,'w',zipfile.ZIP_DEFLATED)
        parentDir = self.getParentDirectory(self.myCharFile)
        for dirPath, dirNames, fileNames in os.walk(parentDir):
            for fileName in fileNames:
                file = os.path.join(dirPath, fileName)
                zf.write(file, file[len(parentDir)+1:])
        zf.close()
        #mp.sendPacket(self.conn_socket, sfileName.encode('utf8'))
        with open(sfileName, 'rb') as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                mp.sendPacket(self.conn_socket, data)
                
        time.sleep(1) # delete after send in fixed len
        mp.sendPacket(self.conn_socket, b'EOF')
        os.remove(sfileName)
    '''
    def sendVersionAndUpdata(self):
        print('send version and updata in image')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, 12348))
        print('updata sock:', sock)
        #arg = (sock, myChafile, friChafile, friendID, callbackfunc)
        updataIfNeed(sock, self.myCharFile, self.friendID, self.setChadisplay, self.callbackfunc)
         
    def getActionPath(self, action_filename):
        path = self.getParentDirectory(self.charFile)
        return path + '/skeleton/'+action_filename
    
    def getSelfActionList(self):
        print(self.myCharFile)
        path = self.getParentDirectory(self.myCharFile) + '/skeleton/'
        anime_list = [f for f in os.listdir(path) if os.path.splitext(f)[1]=='.txt']
        return anime_list
    
    def callbackfunc(self):
        print('callback')
    
    def setChadisplay(self, value=None):
        if value == None:
            return self.charFile
        win32gui.ShowWindow(self.hwnd, value)
        if value == 1:
            self.showAction(self.getActionPath('idle.txt'), repeating = True)
        return None
    
class ChangeImageThread(threading.Thread):
    def __init__(self, win, repeating):
        self.win = win
        self.only_once = not repeating
        self.started = False
        super(ChangeImageThread, self).__init__()
        
    def run(self):
        try:
            while self.win.actionThread is self:
                self.win.SwitchNextImage()
                if self.only_once and self.win.image_index == 0:
                    if self.started:
                        self.win.showAction(self.win.getActionPath('idle.txt'), True)
                    self.started = True
                time.sleep(self.win.GetCurrentImageRemainTime())
        except:pass
        self.win = None
        
if __name__ == '__main__':
    '''
    test codes are too old, try some new codes.
    '''
    win = image_window(lambda:win32gui.PostQuitMessage(0), '123', None, '111.111.111.111', 'data/1/char/1/character1.txt', '1')
    def test(msg):
        win.ShowNewChatMsgWin(msg)
        print(msg,'thread ended')
    
    '''this test cause problems because of using tk in thread'''
    threading.Thread(target=test, args=('Hello, World',)).start()
    #win.uploadCharacter()
    print('uploadCharacter done')
    win32gui.PumpMessages()

 

