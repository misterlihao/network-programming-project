'''
this is a child (a window) of the friend window (a window_list_no_use_now)
'''
import win32con, win32gui, win32api
import struct
from image_window import image_window
import Image
import message_transaction as mt
from win32api import RGB
import tkinter as tk
from tkinter.constants import HORIZONTAL
from pip._vendor.requests.models import CONTENT_CHUNK_SIZE
from tkinter.scrolledtext import ScrolledText

online_indicate_rect = (6,6,16,16)
oir = online_indicate_rect
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

def getXY(lparam):
        return lparam&0xffff, (lparam>>16)&0xffff  
    
class Model:
    '''
    for data storage
    '''
    def __init__(self, ip, friend_name, online, id, email):
        self.set(friend_name, ip, online, id, email)
    
    def set(self, ip, friend_name, online, id, email):
        self.friend_name = friend_name
        self.online = online
        self.friend_id = id
        self.ip = ip
        self.email = email
    
class FriendListItemView:
    '''
    window of friend list item
    '''
    def __init__(self, friend_window_object, _id, friend_name, ip, friend_id, friend_email, w, h):
        '''
        _id is it's win32 id
        friend_name stores the name of the friend it represents
        ip is the friend's address
        '''
        self.model = Model(ip, friend_name, False, friend_id, friend_email)
        self.id = _id
        self.hwnd = win32gui.CreateWindow(
            "window_list_item","",
            win32con.WS_VISIBLE|win32con.WS_CHILD,
            0, 0, 0, 0, friend_window_object.hwnd, _id,
            win32gui.GetModuleHandle(None),
            None)
        
        self.message_map = {
            win32con.WM_DESTROY: self.OnDestroy,
            win32con.WM_COMMAND: self.OnCommand,
            win32con.WM_PAINT: self.OnPaint,
            win32con.WM_SIZE: self.OnSize,
            win32con.WM_RBUTTONUP: self.OnRButtonUp,
        }
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_WNDPROC, self.message_map)
        
        self.chat_btn = win32gui.CreateWindow(
            "Button","chat",
            win32con.WS_VISIBLE|win32con.WS_CHILD|win32con.BS_PUSHBUTTON,
            w-70, 0, 70, 24, self.hwnd, _id,
            win32gui.GetModuleHandle(None),
            None)
        self.friend_window = friend_window_object
    
    def OnSize(self, hwnd, msg, wp, lp):
        w, h = win32api.LOWORD(lp), win32api.HIWORD(lp)
        win32gui.SetWindowPos(self.chat_btn, 0, w-h*3, 0, h*3, h, win32con.SWP_NOZORDER)
        
    def SetFriendData(self, friend_data):
        '''friend_data: a list of form in friendList'''
        self.model.set(*friend_data)
        if self.friend_window.GetChatWin(self.model.friend_id) == None:
            win32gui.SetWindowText(self.chat_btn, 'chat')
        else:
            win32gui.SetWindowText(self.chat_btn, 'close')
        
    def StartChat(self):    
        '''WARNNING!! don't use it anymore. USE StartChat() in frien_window!!'''
        self.friend_window.StartChat(self.model.friend_id)
        
    def OnCommand(self, hwnd, msg, wp, lp):
        '''win32 callback
        ensure you know what you're doing'''
        if (wp>>16)&0xffff == win32con.BN_CLICKED\
            and wp&0xffff == self.id and lp == self.chat_btn:
            try:
                chat_win = self.friend_window.GetChatWin(self.model.friend_id)
                
                if win32gui.IsWindow(chat_win.hwnd):
                    win32gui.DestroyWindow(chat_win.hwnd)
                else:
                    raise Exception()
            except :
                self.friend_window.StartChat(self.model.friend_id)
                win32gui.SetWindowText(self.chat_btn, 'close')
    
    def OnPaint(self, hwnd, msg, wp, lp):
        '''win32 callback
        ensure you know what you're doing'''
        dc, ps = win32gui.BeginPaint(hwnd)
        win32gui.SetBkMode(dc, win32con.TRANSPARENT)
        win32gui.DrawText(dc, self.model.friend_name, -1, (30, 0, 130, 24), win32con.DT_CENTER)
        
        online = self.model.online
        if online:
            brush = win32gui.CreateSolidBrush(RGB(124,193,98))
            oldb = win32gui.SelectObject(dc, brush)
        win32gui.Ellipse(dc,oir[0],oir[1],oir[2],oir[3])
        if online:
            win32gui.SelectObject(dc, oldb)
            win32gui.DeleteObject(brush)
        
        win32gui.EndPaint(hwnd, ps)
        return True
        
    def getCharPath(self, id):
        return 'data/cha/'+id+'/character1.txt'
    
    def IpIsMe(self, ip):
        '''
        check if the ip is the friend this window represents
        '''
        return ip == self.model.ip
    
    def IdIsMe(self, id):
        return id == self.model.friend_id
    
    def OnChatClosed(self):
        '''hand made callback, passed to image_window
        called after image_window closed
        ensure you know what you're doing'''
        '''set button text 'chat' '''
        if win32gui.IsWindow(self.chat_btn):
            win32gui.SetWindowText(self.chat_btn, 'chat')
        
    def OnDestroy(self, hwnd, msg, wp, lp):
        '''win32 callback
        ensure you know what you're doing'''
        return win32gui.DefWindowProc(hwnd, msg, wp, lp)
    
    def OnRButtonUp(self, hwnd, message, wparam, lparam):
        menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(menu, win32con.MF_STRING, 1, 'change name/ip/email')
        win32gui.AppendMenu(menu, win32con.MF_STRING, 2, 'send eamil to '+self.model.friend_name)
        x, y = getXY(lparam)
        x, y = win32gui.ClientToScreen(hwnd, (x, y))
        '''show the popup menu, 0x100 means return item id right after'''
        item_id = win32gui.TrackPopupMenu(menu, 0x100, x, y, 0, hwnd, None)
        if item_id == 1:
            try:
                self.edit_window.destroy()
                self.edit_window = None
            except Exception:
                self.ShowEditWindow()
        elif item_id ==2:
            point = win32gui.GetCursorPos()
            OpenSendEmailWindow(point[0], point[1], self)
                
        win32gui.DestroyMenu(menu)
        return True
    
    def ShowEditWindow(self):
        '''
        show the Edit window.
        this function does not close it even if it's shown.
        '''
        self.edit_window = tk.Tk()
        self.edit_window.overrideredirect(True)
        self.edit_window.wm_attributes('-alpha',1,'-disabled',False,'-toolwindow',True, '-topmost', True)
        frame = tk.Frame(self.edit_window)
        self.input_text = tk.Entry(frame)
        self.input_text.pack(side='left',expand=True, fill='both')
        '''default on change name'''
        self.SwitchToInputName()
        change_btn = tk.Button(frame, text='change', comman=self.CommitChange)
        change_btn.pack(side='right')
        email_btn = tk.Button(frame, text='email', command=self.SwitchToInputEmail)
        email_btn.pack(side='right')
        ip_btn = tk.Button(frame, text='ip', command=self.SwitchToInputIp)
        ip_btn.pack(side='right')
        name_btn = tk.Button(frame, text='name', command=self.SwitchToInputName)
        name_btn.pack(side='right')
        frame.pack()
        
        self.edit_window.geometry('+%d+%d' % self.GetEditWindowPos())
        
    def SwitchToInputName(self):
        '''
        switch entry to name inputting
        '''
        self.input_mode = 0
        self.input_text.delete(0, tk.END)
        self.input_text.insert(0, self.model.friend_name)
        
    def SwitchToInputIp(self):
        '''
        switch entry to ip inputting
        '''
        self.input_mode = 1
        self.input_text.delete(0, tk.END)
        self.input_text.insert(0, self.model.ip)
        
    def SwitchToInputEmail(self):
        '''
        switch entry to email inputting
        '''
        self.input_mode = 2
        self.input_text.delete(0, tk.END)
        self.input_text.insert(0, self.model.email)     
        
    def CommitChange(self):
        if (self.input_mode==1):
            '''self.model.ip still have old ip'''
            self.friend_window.friend_list.ChangeFriendIp(self.model.friend_id, self.input_text.get())
            self.model.ip = self.input_text.get()
            self.input_text.delete(0, tk.END)
            self.input_text.insert(0, 'friend\'s ip changed!')
        elif (self.input_mode==0):
            '''self.model.name still have old name'''
            self.friend_window.friend_list.ChangeFriendName(self.model.friend_id, self.input_text.get())
            self.model.friend_name = self.input_text.get()
            self.input_text.delete(0, tk.END)
            self.input_text.insert(0, 'friend\'s name changed!')
        elif (self.input_mode==2):
            '''self.model.email still have old email'''
            self.friend_window.friend_list.ChangeFriendEmail(self.model.friend_id, self.input_text.get())
            self.model.email = self.input_text.get()
            self.input_text.delete(0, tk.END)
            self.input_text.insert(0, 'friend\'s email changed!')
        win32gui.InvalidateRect(self.hwnd, None, True)
        
    def GetEditWindowPos(self):
        '''control the position of edit window'''
        x = win32gui.GetWindowRect(self.hwnd)[0]
        y = win32gui.GetWindowRect(self.hwnd)[3]
        return x,y
 
class OpenSendEmailWindow:
    def __init__(self, x, y, parent_obeject):
        '''
        create the add friend window.
        '''
        self.parent = parent_obeject
        self.root = tk.Tk()
        self.root.title('Send email to '+parent_obeject.model.friend_name)
        
        self.pane_for_recipient = tk.PanedWindow(self.root,orient=tk.HORIZONTAL, borderwidth=5)
        self.pane_for_recipient.pack(fill=tk.BOTH)
        self.lable_for_recipient = tk.Label(self.pane_for_recipient, text='To:', width=5, justify=tk.LEFT, anchor=tk.W)
        self.entry_for_recipient = tk.Entry(self.pane_for_recipient, width=10)
        self.entry_for_recipient.insert(0, parent_obeject.model.friend_name)
        self.pane_for_recipient.add(self.lable_for_recipient)
        self.pane_for_recipient.add(self.entry_for_recipient)
        
        self.pane_for_topic = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, borderwidth=5)
        self.pane_for_topic.pack(fill=tk.BOTH)
        self.lable_for_topic = tk.Label(self.pane_for_topic, text='Topic:', width=5, justify=tk.LEFT, anchor=tk.W)
        self.entry_for_topic = tk.Entry(self.pane_for_topic, width=10)
        self.pane_for_topic.add(self.lable_for_topic)
        self.pane_for_topic.add(self.entry_for_topic)
        
        self.pane_for_content = tk.PanedWindow(self.root, orient=HORIZONTAL, borderwidth=7)
        self.pane_for_content.pack(fill=tk.BOTH, expand=1)
        self.lable_for_content = tk.Label(self.pane_for_content, text='Text:', justify=tk.LEFT, anchor=tk.W)
        self.text_for_content = ScrolledText(self.pane_for_content, width=10, height=4)
        self.pane_for_content.add(self.lable_for_content)
        self.pane_for_content.add(self.text_for_content)
        
        self.pane_for_button = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.pane_for_button.pack(fill=tk.BOTH)
        self.button_for_add = tk.Button(self.pane_for_button, text="Send", command=self.SendMail)
        self.button_for_close = tk.Button(self.pane_for_button, text="Exit", command=self.Destroy, width=5)
        self.pane_for_button.add(self.button_for_close) 
        self.pane_for_button.add(self.button_for_add)
        
        self.root.geometry('300x200+%d+%d'% (x,y))
        
    def SendMail(self):
        sender = self.parent.friend_window.email
        recipient_name = self.entry_for_recipient.get()
        recipient_email = self.parent.model.email
        topic = self.entry_for_topic.get()
        text = self.text_for_content.get(1.0, tk.END)
        '''call www's function here'''
        '''close after send'''
        self.Destroy()
        print('Sender: ',sender, 'To: ', recipient_email, 'Topic: ', topic)
        print('Text: ', text)
        
    def Destroy(self):
        self.root.destroy() 
    
item_id_acc = 0
def create(friend_window_object, friend_name, ip, friend_id, email, x, y, w, h):
    '''
    return a item window
    should have a parent at creation moment,
    but permanent parent is not required
    '''
    global item_id_acc
    item_id = item_id_acc
    item_id_acc += 1
    
    view = FriendListItemView(friend_window_object, item_id, friend_name,ip, friend_id, email, w, h)
    win32gui.SetWindowPos(view.hwnd, win32con.HWND_TOP, x, y, w, h, win32con.SWP_NOOWNERZORDER)
    return view
        
