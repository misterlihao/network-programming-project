# example1.py
import os
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
wc.cbWndExtra = win32con.DLGWINDOWEXTRA + struct.calcsize("Pi")
# wc.hIconSm = 0
win32gui.RegisterClass(wc)

def getXY(lparam):
    return lparam&0xffff, (lparam>>16)&0xffff

def turnOffTk(tk_object):
    tk_object.destroy()
    #tk_object.quit()

def getCharacter(fileName):
    charFile = open(fileName, 'r')
    charData=[]
    for line in charFile.readlines():       
        charData.append(line.split())
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
    def __init__(self, after_window_close, friend_name, sock, ip, characterFile):
        '''
        sock maybe None, indicates the window is not connected currently.
        '''
        win32gui.InitCommonControls()
        self.hinst = win32api.GetModuleHandle(None)
        '''for show action easy to draw'''
        self.image_index = 0
        '''for show action easy to draw'''
        self.Image_list = []
        self.message_map = {
          win32con.WM_DESTROY: self.OnDestroy,
          win32con.WM_LBUTTONDOWN: self.OnLButtonDown,
          win32con.WM_LBUTTONUP: self.OnLButtonUp,
          win32con.WM_MOVE: self.OnMove,
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
            self.ReadConfig()
        except Exception: 
            self.readCheck=False
            print('no config file')  
        
        self.acting = False
        self.drag_showing = False
        self.dragging = False
        '''history'''
        self.this_messages=[]
        '''for display'''
        self.chat_name = friend_name
        self.history_window_width = 30 # in character
        '''callback function to be execute in ondestroy'''
        self.after = after_window_close
        '''for socket connection'''
        self.ip = ip
        '''the socket , whether connected or not'''
        self.conn_socket = sock
        ''''my character file (path of bitmaps)'''
        self.myCharFile = 'data/cha/character1/character1.txt'
        '''the character file (path of bitmaps)'''
        self.charFile = characterFile
        '''if the socket is connected, not validated already'''
        self.connected = False
        '''the chat msg queue for thread to insert into
           and for main thread to get from'''
        self.chatmsg_queue = queue.Queue()
        '''thread must be correctly terminated in some time (eg: ondestroy)
            and socket must be terminate and released in some time, too'''
        
        self.showAction(self.getActionPath('idle.txt'), True)
        
        if self.conn_socket != None:
            self.DoAfterConnectEstablished()
        '''for selecting the anime to send'''
        self.tmp_anime=""      
        
    def DoAfterConnectEstablished(self):  
        if not self.checkCharVersion():
            self.conn_socket.send('True'.encode('utf8'))
            self.updateCharacter()
        else:
            self.conn_socket.send('False'.encode('utf8'))
        data = self.conn_socket.recv(8192)
        if bool(data=='True'):
            self.uploadCharacter()
            
        thread = threading.Thread(target=self.listen_to_chat_messagesInThread)
        thread.setDaemon(True)
        thread.start()
        self.connected = True
        
    def ReadConfig(self):
        with open(config_file) as file:
            for line in file:
                cap = line.split(":")
                print(cap)
                if cap[0] == 'readCheck':
                    self.readCheck=bool(cap[1]=='True')
                elif cap[0] == 'myCharFile':
                    self.myCharFile = cap[1]
                
    def BuildWindow(self, className):
        style = win32con.WS_POPUP|win32con.WS_VISIBLE
        xstyle = win32con.WS_EX_LAYERED
        
        self.hwnd = win32gui.CreateWindowEx(
                             xstyle,
                             className,
                             "image_window",
                             style,
                             win32con.CW_USEDEFAULT,
                             win32con.CW_USEDEFAULT,
                             130,
                             130,
                             0,
                             0,
                             self.hinst,
                             None)
        win32gui.SetLayeredWindowAttributes(self.hwnd, RGB(255,255,255),0,win32con.LWA_COLORKEY)
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
        if self.drag_showing == False:
            self.showAction(self.getActionPath('click.txt'))
        else:
            self.showAction(self.getActionPath('idle.txt'))
        self.dragging = False
        self.drag_showing = False
        win32gui.ReleaseCapture()
        return True
    def OnMouseMove(self, hwnd, message, wparam, lparam):
        if self.dragging :
            '''old, laggy, working method...
            cur_x, cur_y = win32gui.ClientToScreen(self.hwnd, (win32api.LOWORD(lparam), win32api.HIWORD(lparam))) 
            dx = cur_x-self.drag_point[0]
            dy = cur_y-self.drag_point[1]
            if dx == 0 and dy == 0:
                return True
            if not self.drag_showing:
                self.drag_showing = True
                self.showAction(self.getActionPath('drag.txt'), True)
            x,y = self.drag_pre_pos'''
            
            '''not tested method'''
            cur_x, cur_y = win32gui.ClientToScreen(self.hwnd, (win32api.LOWORD(lparam), win32api.HIWORD(lparam))) 
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
            
            win32gui.SetWindowPos(self.hwnd, 0, x+dx, y+dy, 0, 0, win32con.SWP_NOSIZE|win32con.SWP_NOOWNERZORDER)
        return True
    def OnRButtonUp(self, hwnd, message, wparam, lparam):
        menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(menu, win32con.MF_STRING, 1, 'speak')
        win32gui.AppendMenu(menu, win32con.MF_STRING, 2, 'read check')
        win32gui.AppendMenu(menu, win32con.MF_STRING, 3, 'historical messages')
        win32gui.AppendMenu(menu, win32con.MF_STRING, 4, 'close')
        if self.readCheck == True: #check new menu's mark
            win32gui.CheckMenuItem(menu, 2, win32con.MF_CHECKED)
        x, y = getXY(lparam)
        x, y = win32gui.ClientToScreen(hwnd, (x, y))
        '''show the popup menu, 0x100 means return item id right after'''
        item_id = win32gui.TrackPopupMenu(menu, 0x100, x, y, 0, hwnd, None)
        if item_id == 1:
            try:
                turnOffTk(self.speak_window)
                self.speak_window = None
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
        win32gui.DestroyMenu(menu)
        return True
    
    def OnMove(self, hwnd, message, wparam, lparam):
        '''
        called when window is moved.
        control things here
        '''
        try:self.speak_window.geometry('+%d+%d' % self.GetSpeakWindowPos())
        except Exception:pass
        return win32gui.DefWindowProc(hwnd, message, wparam, lparam)
        
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
        
        self.speak_window.geometry('+%d+%d' % self.GetSpeakWindowPos())
        self.speak_window.mainloop()
    def InputTextHitReturn(self, event):
        self.SendText()
        
    def GetHistoryWindowPos(self):
        '''control the position of history window'''
        return win32gui.GetCursorPos()
    
    def GetHistoryString(self):
        '''
        read histroy file and make it pretty
        return a prettt string for histroy window display
        '''
        s = ''
        try:
            with open('history') as file:
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
        self.history_window.mainloop()
    
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
            anime_list = ['anime 1','anime 2']
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
        print ("selection:", selection, ": '%s'" % value)
        
    def SendText(self):
        '''
        SendText to remote chatter'''
        if self.conn_socket == None:
            self.conn_socket = mt.StartTalking(self.ip)
            if self.conn_socket == None:
                return 
            self.DoAfterConnectEstablished() 
        
        self.conn_socket.send(self.input_text.get().encode('utf8'))
        mt.SendAnime(self.tmp_anime, self.conn_socket)
        self.this_messages.append(self.input_text.get())
        
        self.input_text.delete(0, tk.END)
        self.showAction(self.getActionPath('send.txt'))
        
    def OnPaint(self, hwnd, message, wparam, lparam):
        dc,ps = win32gui.BeginPaint(hwnd)
        if len(self.Image_list)>0:
            self.Image_list[self.image_index].draw_on_dc(dc, RGB(255,255,255))
        win32gui.EndPaint(hwnd, ps)
        return True
    def OnDestroy(self, hwnd, message, wparam, lparam):
        '''
        kill all tk things here
        '''
        with open(config_file, 'w') as file:
            file.write('readCheck:'+str(self.readCheck))
            file.write('myCharFile:'+str(self.myCharFile))
        with open(history_file, 'a') as file:
            for each in self.this_messages:
                file.write(each+'\n')
       
        try:turnOffTk(self.speak_window)
        except :pass
        try:turnOffTk(self.history_window)
        except :pass
        self.after()
        
        self.actionThread = None
        print('image_window on destroy')
        return True
    def getCharFile(self):
        return self.charFile
    def showAction(self, skelFile, repeating = False, acting=True):
        '''
        show an action
        the acting parameter should not be used by public user.
        '''
        skelData=[]
        print(skelFile)
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
        if acting:
            self.acting = True
            self.actionThread = ChangeImageThread(self, repeating)
            self.actionThread.setDaemon(True)
            self.actionThread.start()
        else:
            self.acting = False
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
                msg = self.conn_socket.recv(1000)
                if msg == b"":
                    raise Exception()
            except:
                print('recv fail')
                return
            msg = msg.decode('utf8')
            '''send the message to next stage .Control the timing here'''
            self.chatmsg_queue.put(msg)
            win32gui.SendMessage(self.hwnd, WM_CHATMSGRECV, 0, 0)
    
    def OnChatMessageReceived(self, hwnd, win32msg, wp, lp):
        '''
        Called when recv msg
        it's in the main thread, so dealing with gui is safe.
        
        maybe add histroy here
        '''
        msg = self.chatmsg_queue.get()
        print('%s: %s'%(self.chat_name,msg))

    def getParentDirectory(self, path):
        #return os.path.abspath(os.path.join(path, os.pardir))
        path2 = path.split('/')
        temp=''
        for ph in path2:
            if(len(ph)>4 and (ph[len(ph)-4:] == '.txt')):
                break
            temp = os.path.join(temp, ph)         
        return temp

    def getArchiveName(self, path):
        path2 = path.split('/')
        for ph in path2:
            if(len(ph)>4 and (ph[len(ph)-4:] == '.txt')):
                return ph[:len(ph)-4]+'.zip'
        return 'ArchiveName.zip'
                
    def cmpCharVersion(self, myDataSize = 0, hisDataSize = 0):
        print('mysize:'+str(myDataSize))
        print('hissize:'+str(hisDataSize))
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
        print('check Character ...')
        text = str(self.getCharDataSize(self.getParentDirectory(self.myCharFile)))
        self.conn_socket.send(text.encode('utf8'))
        data = self.conn_socket.recv(8192).decode('utf8')
        if self.cmpCharVersion(self.getCharDataSize(self.getParentDirectory(self.charFile)), int(data)):
            return True
        return False

    def updateCharacter(self):
        print('update Character ...')
        fileName = self.conn_socket.recv(4096).decode('utf8')
        with open(fileName, 'wb') as cfile:
            while True:
                data = self.conn_socket.recv(4096)
                if data == b'EOF':
                    print('recv file success!')
                    break
                cfile.write(data)

        win32gui.ShowWindow(self.hwnd, 0)
        os.system('rd /S /Q ' + self.getParentDirectory(self.charFile))
        zf = zipfile.ZipFile(fileName)
        zf.extractall(self.getParentDirectory(self.charFile))
        print('update success')
        zf.close()
        win32gui.ShowWindow(self.hwnd, 1)
        os.remove(fileName)
        
    def uploadCharacter(self):
        print('upload Character ...')
        sfileName = self.getArchiveName(self.myCharFile)
        zf = zipfile.ZipFile(sfileName,'w',zipfile.ZIP_DEFLATED)
        for dirPath, dirNames, fileNames in os.walk(sfileName):
            for fileName in fileNames:
                file = os.path.join(dirPath, fileName)
                zf.write(file, file[len(sfileName)+1:])
        zf.close()
        self.conn_socket.send(sfileName.encode('utf8'))
        with open(sfileName, 'rb') as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                self.conn_socket.send(data)
                
        self.conn_socket.send(b'EOF')
        print('send success!')
        os.remove(sfileName)
        
            
    def getActionPath(self, action_filename):
        path = self.getParentDirectory(self.charFile)
        return path + '/skeleton/'+action_filename

    
def getSkelFile():
    return 'data/cha/1/skeleton/skeleton6.txt'

class ChangeImageThread(threading.Thread):
    def __init__(self, win, repeating):
        self.win = win
        self.only_once = not repeating
        self.started = False
        super(ChangeImageThread, self).__init__()
        
    def run(self):
        try:
            while self.win.actionThread is self:
                #print('switch image')
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

    win = image_window(lambda:win32gui.PostQuitMessage(0), '123', None, '111.111.111.111', 'data/cha/character1/character1.txt')
    win.showAction('data/cha/1/skeleton/send.txt')
    #win.uploadCharacter()
    print('uploadCharacter done')
    win32gui.PumpMessages()

 

