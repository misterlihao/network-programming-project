'''
not used now. maybe future
A hand-made list of windows
'''
import win32con, win32gui, win32api
import struct

class WindowList:
    def __init__(self, parent, x, y, w, h): 
        self.items = []
        self.hinst = win32api.GetModuleHandle(None)
        self.hwnd = None
        self.message_map = {
          win32con.WM_DESTROY: self.OnDestroy,
          win32con.WM_COMMAND: self.OnCommand,
        }
        cn = self.RegisterClass()
        self.BuildWindow(cn, parent, x, y, w, h)
    def RegisterClass(self):
        className = "window_list_window"
        wc = win32gui.WNDCLASS()
        wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wc.lpfnWndProc = self.message_map
        wc.cbWndExtra = 0
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32con.BLACK_BRUSH
        wc.hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        wc.lpszClassName = className
        wc.cbWndExtra = win32con.DLGWINDOWEXTRA + struct.calcsize("Pi")
        win32gui.RegisterClass(wc)
        return className

    def BuildWindow(self, className, parent, x, y, w, h):
        style = win32con.WS_VISIBLE|win32con.WS_CHILD
        self.hwnd = win32gui.CreateWindow(
                             className, "list_window", style,
                             x, y, w, h, parent, 0, self.hinst, None)
        
    def InsertItem(self, *hwnd_and_ids):
        '''
        will change item's parent to itself
        must be called to inform that an item needs to be arranged
        '''
        for hwnd, item_id in hwnd_and_ids:
            self.items.append((hwnd, item_id))
            win32gui.SetParent(hwnd, self.hwnd)
        
    def OnCommand(self, hwnd, msg, wp, lp):
        return win32gui.DefWindowProc(hwnd, msg, wp, lp)
    
    def OnDestroy(self, hwnd, msg, wp, lp):
        return True
