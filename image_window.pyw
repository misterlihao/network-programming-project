# example1.py
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

def RGB(r, g, b):
    r = r & 0xFF
    g = g & 0xFF
    b = b & 0xFF
    return (b << 16) | (g << 8) | r

def getXY(lparam):
    return lparam&0xffff, (lparam>>16)&0xffff

def turnOffTk(tk_object):
    tk_object.destroy()
    tk_object.quit()

def getCharacter(fileName):
    charFile = open(fileName, 'r')
    charData=[]
    length, height = charFile.readline().split()
    for line in charFile.readlines():       
        charData.append(line.split())
    charFile.close()
    return int(length), int(height), charData

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
    def __init__(self, after_window_close, sock, ip, characterFile='data/character1.txt'):
        '''
        sock maybe None, indicates the window is not connected currently.
        '''
        win32gui.InitCommonControls()
        self.hinst = win32api.GetModuleHandle(None)
        self.image_index = 0
        self.Image_list = []
        self.message_map = {
          win32con.WM_DESTROY: self.OnDestroy,
          win32con.WM_LBUTTONDOWN: self.OnLButtonDown,
          win32con.WM_PAINT: self.OnPaint,
          win32con.WM_RBUTTONUP: self.OnRButtonUp,
          win32con.WM_MOVE: self.OnMove,
        }
        try:
            self.ReadConfig()
        except Exception: 
            self.readCheck=False
            print('no config file')  

        self.this_messages=[]
        self.chat_name = 'Friend A'
        self.history_window_width = 30 # in character
        self.after = after_window_close
        self.ip = ip
        self.conn_socket = sock
        self.charFile = characterFile
    def ReadConfig(self):
        with open(config_file) as file:
            for line in file:
                cap = line.split(":")
                print(cap)
                if cap[0] == 'readCheck':
                    self.readCheck=bool(cap[1]=='True')
                    break
    def CreateWindow(self):
        self.BuildWindow("image_window")
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_WNDPROC, self.message_map)
        
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
        self.Image_list = Image_list
        self.image_index = 0
    
    def SwitchNextImage(self):
        '''maybe call Resize here'''
        self.image_index = (self.image_index+1)%len(self.Image_list)
        
        #redrawing
        win32gui.InvalidateRect(self.hwnd, None, True)
    
    def GoOnTop(self):
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOMOVE|win32con.SWP_NOSIZE)
    def StayTop(self):
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE|win32con.SWP_NOSIZE)
    def Resize(self, w, h):
        win32gui.SetWindowPos(self.hwnd, 0, 0, 0, w, h, win32con.SWP_NOMOVE|win32con.SWP_NOOWNERZORDER)
    
    def OnNCCreate(self, hwnd, message, wparam, lparam):
        '''
        DO NOT edit things here unless you really know what you're doing
        '''
        return True
    
    def OnLButtonDown(self, hwnd, message, wparam, lparam):
        win32api.SendMessage(hwnd, win32con.WM_NCLBUTTONDOWN, 2, lparam)
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
        item_id = win32gui.TrackPopupMenu(menu, 0x100, x, y, 0, hwnd, None) #0x100 means return item id right after
        if item_id == 1:
            if self.conn_socket == None:
                if oc.CheckSomeoneOnline(self.ip) == False:
                    print('He is Offline')
                else:
                    self.conn_socket = mt.StartTalking(self.ip)
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
        
    def GetSpeakWindowPos(self):
        x = win32gui.GetWindowRect(self.hwnd)[0]
        y = win32gui.GetWindowRect(self.hwnd)[3]
        return x,y
    
    def ShowSpeakWindow(self):
        '''
        show the speaking window.
        this function does not close it when it's shown.
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
        self.history_window = tk.Tk()
        self.history_window.wm_attributes('-toolwindow',True)
        self.history_window.resizable(width=False, height=False)
        self.history_window.title('[%s] %s' % ('HISTORY', self.chat_name))
        
        text = tk.Text(self.history_window,
                       exportselection=0,
                       width=self.history_window_width,
                       height=10)
        text.insert(tk.END, self.GetHistoryString())
        text.config(state=tk.DISABLED)
        text.pack(side='left',fill='y')
        
        scrollbar = tk.Scrollbar(self.history_window)
        scrollbar.pack(side='right', fill='y')
        
        text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text.yview)
        
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
        else:
            anime_list = ['anime 1','anime 2']
            self.anime_lb = tk.Listbox(self.speak_window, height = len(anime_list))
            for i in range(len(anime_list)):
                self.anime_lb.insert(i+1, anime_list[i])
            self.anime_lb.pack(expand=True, fill='both')
        
    def SendText(self):
        '''
        SendText to remote chatter
        '''
        self.conn_socket.send(self.input_text.get().encode('utf8'))
        self.this_messages.append(self.input_text.get())
        
        self.input_text.delete(0, tk.END)
        
    def OnPaint(self, hwnd, message, wparam, lparam):
        dc,ps = win32gui.BeginPaint(hwnd)
        self.Image_list[self.image_index].draw_on_dc(dc, RGB(255,255,255))
        win32gui.EndPaint(hwnd, ps)
        return True
    def OnDestroy(self, hwnd, message, wparam, lparam):
        '''
        kill all tk things here
        '''
        with open(config_file, 'w') as file:
            file.write('readCheck:'+str(self.readCheck))
        with open(history_file, 'a') as file:
            for each in self.this_messages:
                file.write(each+'\n')
       
        try:turnOffTk(self.speak_window)
        except Exception:pass
        try:turnOffTk(self.history_window)
        except Exception:pass
        self.after()
        
        return True
    def getCharFile(self):
        return self.charFile
    def showAction(self, skelFile, acting=True):
        '''
        show an action
        the acting parameter should not be used by public user.
        '''
        skelData=[]
        charFile = open(skelFile, 'r')   
        for line in charFile.readlines():
            skelData.append(line.split())
        charFile.close()    
        
        x_size, y_size, charData = getCharacter(self.getCharFile())
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
            myThread = threading.Thread(target = func, args=(self,))
            myThread.setDaemon(True)
            myThread.start()
    def showCharacter(self, skelFile):
        '''
        show a animation with only one action
        '''
        self.showAction(skelFile, False)
    def OnChatMessageReceived(self, msg):
        '''
        Called when recv msg
        it's in the main thread, so dealing with gui is safe.
        
        maybe add histroy here
        '''
        tkmb.showinfo('new message', msg)

def getSkelFile():
    return 'data/skeleton5.txt'
def func(*args):
    win,= args
    while True:
        time.sleep(0.15)
        win.SwitchNextImage()

if __name__ == '__main__':
    '''
    test codes are too old, try some new codes.
    '''
