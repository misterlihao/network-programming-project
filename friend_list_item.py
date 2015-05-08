'''
this is a child (a window) of the friend window (a window_list_no_use_now)
'''
import win32con, win32gui, win32api
import struct
from image_window import image_window
import Image
#execute once
className = "window_list_item"
wc = win32gui.WNDCLASS()
wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
wc.lpfnWndProc = win32gui.DefWindowProc
wc.cbWndExtra = 0
wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
wc.hbrBackground = win32con.BLACK_BRUSH
wc.hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
wc.lpszClassName = className
wc.cbWndExtra = win32con.DLGWINDOWEXTRA + struct.calcsize("Pi")
win32gui.RegisterClass(wc)

class Model:
    def __init__(self, friend_name):
        self.friend_name = friend_name
    
class View:
    def __init__(self, parent, _id, friend_name):
        self.model = Model(friend_name)
        self.id = _id
        self.chat_win = None
        self.hwnd = win32gui.CreateWindow(
            "window_list_item","",
            win32con.WS_VISIBLE|win32con.WS_CHILD,
            0, 0, 0, 0, parent, _id,
            win32gui.GetModuleHandle(None),
            None)
        
        self.message_map = {
            win32con.WM_DESTROY: self.OnDestroy,
            win32con.WM_COMMAND: self.OnCommand,
            win32con.WM_PAINT: self.OnPaint,
        }
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_WNDPROC, self.message_map)
        
        self.chat_btn = win32gui.CreateWindow(
            "Button","chat",
            win32con.WS_VISIBLE|win32con.WS_CHILD|win32con.BS_PUSHBUTTON,
            130, 0, 70, 24, self.hwnd, _id,
            win32gui.GetModuleHandle(None),
            None)
    def OnCommand(self, hwnd, msg, wp, lp):
        print('command ', self.id)
        if (wp>>16)&0xffff == win32con.BN_CLICKED\
            and wp&0xffff == self.id and lp == self.chat_btn:
            try:
                if win32gui.IsWindow(self.chat_win.hwnd):
                    win32gui.DestroyWindow(self.chat_win.hwnd)
                else:
                    self.StartChat()
            except :
                self.StartChat()
    
    def OnPaint(self, hwnd, msg, wp, lp):
        dc, ps = win32gui.BeginPaint(hwnd)
        win32gui.SetBkMode(dc, win32con.TRANSPARENT)
        win32gui.DrawText(dc, self.model.friend_name, -1, (30, 0, 130, 24), win32con.DT_CENTER)
        win32gui.EndPaint(hwnd, ps)
    def StartChat(self):
        '''
        Create a image_window here
        '''
        win32gui.SetWindowText(self.chat_btn, 'close')
        self.chat_win = image_window(self.OnChatClosed)
        self.chat_win.CreateWindow()
        self.chat_win.Resize(256, 128)
        hbmp1 = win32gui.LoadImage(0, 'shime1.bmp', win32gui.IMAGE_BITMAP, 0, 0,win32gui.LR_LOADFROMFILE)
        hbmp2 = win32gui.LoadImage(0, 'shime2.bmp', win32gui.IMAGE_BITMAP, 0, 0,win32gui.LR_LOADFROMFILE)
        img1 = Image.Image()
        img1.append_component(hbmp1, 0, 0, 128, 128)
        img1.append_component(hbmp2, 128, 0, 128, 128)
        img2 = Image.Image()
        img2.append_component(hbmp2, 0, 0, 128, 128)
        img2.append_component(hbmp1, 128, 0, 128, 128)
        self.chat_win.SetImages([img1, img2])
        
    def OnChatClosed(self):
        win32gui.SetWindowText(self.chat_btn, 'chat')
        self.chat_win = None
        
    def OnDestroy(self, hwnd, msg, wp, lp):
        return win32gui.DefWindowProc(hwnd, msg, wp, lp)
    
item_id_acc = 0
def create(parent, friend_name, x, y, w, h):
    '''
    return a item window handle, unique id
    should have a parent, permanent parent is not required
    '''
    global item_id_acc
    item_id = item_id_acc
    item_id_acc += 1
    
    view = View(parent, item_id, friend_name)
    win32gui.SetWindowPos(view.hwnd, win32con.HWND_TOP, x, y, w, h, win32con.SWP_NOOWNERZORDER)
    return view
        