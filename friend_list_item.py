'''
this is a child (a window) of the friend window (a window_list_no_use_now)
'''
import win32con, win32gui, win32api
import struct
from image_window import image_window, getSkelFile
import Image
import message_transaction as mt
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
    '''
    for data storage
    '''
    def __init__(self, friend_name, ip):
        self.friend_name = friend_name
        self.ip = ip
    
class FriendListItemView:
    '''
    window of friend list item
    '''
    def __init__(self, parent, _id, friend_name, ip):
        '''
        _id is it's win32 id
        friend_name stores the name of the friend it represents
        ip is the friend's address
        '''
        self.model = Model(friend_name, ip)
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
        '''win32 callback
        ensure you know what you're doing'''
        print('command ', self.id)
        if (wp>>16)&0xffff == win32con.BN_CLICKED\
            and wp&0xffff == self.id and lp == self.chat_btn:
            try:
                if win32gui.IsWindow(self.chat_win.hwnd):
                    win32gui.DestroyWindow(self.chat_win.hwnd)
                else:
                    raise Exception()
            except :
                try:
                    sock = mt.StartTalking(self.model.ip)
                    self.StartChat(sock)
                except:
                    print(self.model.ip, 'is offline')
                    self.StartChat()
    
    def OnPaint(self, hwnd, msg, wp, lp):
        '''win32 callback
        ensure you know what you're doing'''
        dc, ps = win32gui.BeginPaint(hwnd)
        win32gui.SetBkMode(dc, win32con.TRANSPARENT)
        win32gui.DrawText(dc, self.model.friend_name, -1, (30, 0, 130, 24), win32con.DT_CENTER)
        win32gui.EndPaint(hwnd, ps)
    def StartChat(self, sock=None):
        '''
        Create a image_window here
        should be the only entrance of image_window
        supposed just called once before a corresponding win32gui.DestroyWindow
        '''
        win32gui.SetWindowText(self.chat_btn, 'close')
        self.chat_win = image_window(self.OnChatClosed, self.model.friend_name, sock, self.model.ip)
        self.chat_win.showCharacter(getSkelFile())
    
    def IsMe(self, ip):
        '''
        check if the ip is the friend this window represents
        '''
        return ip == self.model.ip
    
    def OnChatClosed(self):
        '''hand made callback, passed to image_window
        called after image_window closed
        ensure you know what you're doing'''
        '''set button text 'chat' '''
        win32gui.SetWindowText(self.chat_btn, 'chat')
        '''for next open'''
        self.chat_win = None
        
    def OnDestroy(self, hwnd, msg, wp, lp):
        '''win32 callback
        ensure you know what you're doing'''
        return win32gui.DefWindowProc(hwnd, msg, wp, lp)
    
item_id_acc = 0
def create(parent, friend_name, ip, x, y, w, h):
    '''
    return a item window
    should have a parent at creation moment,
    but permanent parent is not required
    '''
    global item_id_acc
    item_id = item_id_acc
    item_id_acc += 1
    
    view = FriendListItemView(parent, item_id, friend_name,ip)
    win32gui.SetWindowPos(view.hwnd, win32con.HWND_TOP, x, y, w, h, win32con.SWP_NOOWNERZORDER)
    return view
        
