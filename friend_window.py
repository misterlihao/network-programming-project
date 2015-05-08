'''
@author: misterlihao
This is supposed to be main window
'''
from image_window import image_window
import friend_list_item
import win32gui, win32api, win32con
import struct
import time

def create_image_window(character_path):
    pass

class FriendWin:
    def __init__(self): 
        win32gui.InitCommonControls()
        self.hinst = win32api.GetModuleHandle(None)
        self.message_map = {
          win32con.WM_DESTROY: self.OnDestroy,
          win32con.WM_SYSCOMMAND: self.OnSysCommand,
        }
        cn = self.RegisterClass()
        self.BuildWindow(cn)
        
        rect = win32gui.GetClientRect(self.hwnd)
        self.friend_list = []
        fn = list('abcdefghij')
        for i in range(10):
            friend = friend_list_item.create(self.hwnd, fn[i]*10, 0, 24*i, rect[2], 24)
            self.friend_list.append(friend)
        
        win32gui.ShowWindow(self.hwnd, win32con.SW_NORMAL)
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
        '''if wp == win32con.SC_MINIMIZE:
            win32gui.ShowWindow(self.hwnd, 0)
            time.sleep(2)
            win32gui.ShowWindow(self.hwnd, 1)
            return True
        '''
        return win32gui.DefWindowProc(hwnd, msg, wp, lp)
    
    def OnDestroy(self, hwnd, msg, wp, lp):
        win32gui.PostQuitMessage(0)
        return True

if __name__ == '__main__':
    mainwin = FriendWin()
    win32gui.PumpMessages()
    print('end')