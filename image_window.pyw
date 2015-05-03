# example1.py
import struct
import win32api
import win32con
import win32gui

import tkinter as tk
import tkinter.messagebox as tkmb
import threading
import time

config_file="config"
registered = False

def RGB(r, g, b):
    r = r & 0xFF
    g = g & 0xFF
    b = b & 0xFF
    return (b << 16) | (g << 8) | r

def getXY(lparam):
    return lparam&0xffff, (lparam>>16)&0xffff

class image_window:
    '''
    modify .message_map to handle messages
    init is the constructor
    stuck in run() and released after closed
    SetImages() to set a list of paths
    SwitchNextImage() let you switch to next image
    '''
    '''
    TODO 
    sending message
    allowing multiline message
    preview anime
    '''
    def __init__(self):
        win32gui.InitCommonControls()
        self.hinst = win32api.GetModuleHandle(None)
        self.bmp = None
        self.image_index = -1
        self.image_paths = ['shime1.bmp', 'shime2.bmp']
        self.message_map = {
          win32con.WM_DESTROY: self.OnDestroy,
          win32con.WM_LBUTTONDOWN: self.OnLButtonDown,
          win32con.WM_PAINT: self.OnPaint,
          win32con.WM_RBUTTONUP: self.OnRButtonUp,
          win32con.WM_MOVE: self.OnMove,
        }
        self.readCheck=False
        with open(config_file) as file:
            for line in file:
                cap = line.split(":")
                print(cap)
                if cap[0] == 'readCheck':
                    self.readCheck=bool(cap[1]=='True')
                    print(self.readCheck)
                    break
    def CreateWindow(self):
        global registered
        if registered == False:
            registered = True
            self.RegisterClass()
        self.BuildWindow("image_window")
    def RegisterClass(self):
        className = "image_window"
        wc = win32gui.WNDCLASS()
        wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wc.lpfnWndProc = self.message_map
        wc.cbWndExtra = 0
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32con.COLOR_WINDOW + 1
        wc.hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        wc.lpszClassName = className
        wc.cbWndExtra = win32con.DLGWINDOWEXTRA + struct.calcsize("Pi")
        # wc.hIconSm = 0
        classAtom = win32gui.RegisterClass(wc)
        return className

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
    def SetImages(self, paths):
        self.image_paths = paths
        self.image_index = -1
    
    def SwitchNextImage(self):
        if self.bmp!= None:
            win32gui.DeleteObject(self.bmp)
        self.image_index = (self.image_index+1)%len(self.image_paths)
        self.bmp = win32gui.LoadImage(0, self.image_paths[self.image_index], win32gui.IMAGE_BITMAP, 0, 0,win32gui.LR_LOADFROMFILE)
        
        pybmp = win32gui.GetObject(self.bmp)
        w = pybmp.bmWidth
        h = pybmp.bmHeight
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, 0, 0, w, h, win32con.SWP_NOMOVE)
        win32gui.InvalidateRect(self.hwnd, None, True)
        
    def OnNCCreate(self, hwnd, message, wparam, lparam):
        return True
    
    def OnLButtonDown(self, hwnd, message, wparam, lparam):
        win32api.SendMessage(hwnd, win32con.WM_NCLBUTTONDOWN, 2, lparam)
        return True
    
    def OnRButtonUp(self, hwnd, message, wparam, lparam):
        menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(menu, win32con.MF_STRING, 1, 'speak')
        win32gui.AppendMenu(menu, win32con.MF_STRING, 2, 'read check')
        if self.readCheck == True: #check new menu's mark
            win32gui.CheckMenuItem(menu, 2, win32con.MF_CHECKED)
        x, y = getXY(lparam)
        x, y = win32gui.ClientToScreen(hwnd, (x, y))
        id = win32gui.TrackPopupMenu(menu, 0x100, x, y, 0, hwnd, None) #0x100 means return item id right after
        if id == 1:
            if hasattr(self, 'speak_window') and self.speak_window != None\
                and self.speak_window.state() == tk.NORMAL:
                self.speak_window.destroy()
                self.speak_window.quit()
                self.speak_window = None
            else:
                self.ShowSpeakWindow()
        if id == 2:
            self.readCheck=not self.readCheck
        print('huh, finally released')
        win32gui.DestroyMenu(menu)
    
    def OnMove(self, hwnd, message, wparam, lparam):
        if hasattr(self, 'speak_window') and self.speak_window != None\
                and self.speak_window.state() == tk.NORMAL:
            self.speak_window.geometry('+%d+%d' % self.GetSpeakingWindowPos())
        
    def GetSpeakingWindowPos(self):
        x = win32gui.GetWindowRect(self.hwnd)[0]
        y = win32gui.GetWindowRect(self.hwnd)[3]
        return x,y
    
    def ShowSpeakWindow(self):
        self.speak_window = tk.Tk()
        self.speak_window.overrideredirect(True)
        self.speak_window.wm_attributes('-alpha',1,'-disabled',False,'-toolwindow',True, '-topmost', True)
        frame = tk.Frame(self.speak_window)
        input_text = tk.Entry(frame)
        input_text.pack(side='left')
        send_btn = tk.Button(frame, text='send', command=self.SendText)
        send_btn.pack(side='right')
        anime_btn = tk.Button(frame, text='anime', command=self.SelectAnime)
        anime_btn.pack(side='right')
        frame.pack()
        
        self.speak_window.geometry('+%d+%d' % self.GetSpeakingWindowPos())
        self.speak_window.mainloop()
    
    def SelectAnime(self):
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
        self.speak_window.destroy()
        '''send something here'''
#         tkmb.showinfo('title', 'message')
    
    def OnPaint(self, hwnd, message, wparam, lparam):
        if (self.bmp == None):
            return False
#         print('on paint')
        dc,ps = win32gui.BeginPaint(hwnd)
        
        mdc = win32gui.CreateCompatibleDC(dc)
        win32gui.SelectObject(mdc,self.bmp)
        pybmp = win32gui.GetObject(self.bmp)
        w = pybmp.bmWidth
        h = pybmp.bmHeight
        win32gui.TransparentBlt(dc, 0, 0, w, h, mdc, 0, 0, w, h, RGB(255,255,255))
        win32gui.DeleteDC(mdc)
        
        win32gui.EndPaint(hwnd, ps)
        return True
    def OnDestroy(self, hwnd, message, wparam, lparam):
        with open(config_file, 'w') as file:
            file.write('readCheck:'+str(self.readCheck))
        after_window_closed()
        if hasattr(self, 'speak_window') and self.speak_window != None:
            self.speak_window.quit()
        return True

win = image_window()
def func():
    global win
    while True:
        time.sleep(0.3)
        win.SwitchNextImage()
def after_window_closed():
    win32gui.PostQuitMessage(0)
    
if __name__ == '__main__':
    win.CreateWindow()
    win.SetImages(['shime1.bmp','shime2.bmp', 'shime3.bmp'])
    win.SwitchNextImage()
    threading.Thread(target = func).start()
    win32gui.PumpMessages()
    print('end')
