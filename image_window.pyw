# example1.py
import sys
sys.path.append('.\win32\lib')
sys.path.append('.\win32')
import struct
import win32api
import win32con
import win32gui

import tkinter as tk
import tkinter.messagebox as tkmb
import threading
import time

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
    choose anime
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
        }
    def CreateWindow(self):
        className = self.RegisterClass()
        self.BuildWindow(className)
    def run(self):
        win32gui.PumpMessages()
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
        ''' C code: wc.cbWndExtra = DLGWINDOWEXTRA + sizeof(HBRUSH) + 
(sizeof(COLORREF));'''
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
        x, y = getXY(lparam)
        x, y = win32gui.ClientToScreen(hwnd, (x, y))
        id = win32gui.TrackPopupMenu(menu, 0x100, x, y, 0, hwnd, None) #0x100 means return item id right after
        if id == 1:
            self.ShowSpeakWindow()
        print('huh, finally released')
        
    def ShowSpeakWindow(self):
        self.speak_window = tk.Tk()
        self.speak_window.overrideredirect(True)
        self.speak_window.wm_attributes('-alpha',1,'-disabled',False,'-toolwindow',True, '-topmost', True)
        input_text = tk.Entry(self.speak_window)
        input_text.pack(side='left')
        send_btn = tk.Button(self.speak_window, text='send', command=self.SendText)
        send_btn.pack(side='right')
        anime_btn = tk.Button(self.speak_window, text='anime', command=self.SelectAnime)
        anime_btn.pack(side='right')
        w = 220
        h = 20
        print(win32gui.GetWindowRect(self.hwnd)[3])
        x = win32gui.GetWindowRect(self.hwnd)[0]
        y = win32gui.GetWindowRect(self.hwnd)[3]
        self.speak_window.geometry('%dx%d+%d+%d' % (w,h,x,y))
        self.speak_window.mainloop()
    
    def SelectAnime(self):
        pass
        
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
        win32gui.PostQuitMessage(0)
        return True

win = image_window()
def func():
    global win
    while True:
        time.sleep(0.3)
        win.SwitchNextImage()
if __name__ == '__main__':
    win.CreateWindow()
    win.SetImages(['shime1.bmp','shime2.bmp', 'shime3.bmp'])
    win.SwitchNextImage()
    threading.Thread(target = func).start()
    win.run()#stuck here
    print('end')
