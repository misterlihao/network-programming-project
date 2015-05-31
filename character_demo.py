# example1.py
import os
import struct
import win32api
import win32con
import win32gui
import threading
import Image
import time
import message_transaction as mt
from win32api import RGB
from tkinter import Entry
import elfAutoBehavior
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
    def __init__(self, after_window_close, characterFile):
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
        }
        '''create the window '''
        self.BuildWindow("image_window")
        '''set the message mapping '''
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_WNDPROC, self.message_map)
        '''read the configurations from file'''
        self.autoBehave = False
        '''whether the drag action is showing'''
        self.drag_showing = False
        '''whether character is being dragged''' 
        self.dragging = False
        '''callback function to be execute in ondestroy'''
        self.after = after_window_close
        '''the character file (path of bitmaps)'''
        self.charFile = characterFile
        self.showAction(self.getActionPath('idle.txt'), True)
        self.actionNow = None
        actionList = self.getAutoBehaviorActions()
        self.elfAutoBehaviorThread = elfAutoBehavior.ElfAutoBehavior(self, actionList)
        self.elfAutoBehaviorThread.setDaemon(True)
        self.elfAutoBehaviorThread.start()
    
    def getAutoBehaviorActions(self):
        path = self.getParentDirectory(self.charFile) + '/skeleton/'
        anime_list = [f for f in os.listdir(path) if os.path.splitext(f)[1]=='.txt']
        with open(path+'autoBehave.config') as file:
            accept_list = [line[:-1] for line in file] 
        result_list = ['walk.txt']
        for anime in anime_list:
            print(anime)
            if accept_list.count(anime) > 0:
                result_list.append(anime)
                
        return result_list
    
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
    
    def OnLButtonDown(self, hwnd, message, wparam, lparam):
        self.dragging = True
        self.drag_point = win32gui.ClientToScreen(self.hwnd, (win32api.LOWORD(lparam), win32api.HIWORD(lparam)))
        self.drag_pre_pos =  win32gui.ClientToScreen(self.hwnd, (0,0))
        win32gui.SetCapture(hwnd)
        return True
    
    def OnLButtonUp(self, hwnd, message, wparam, lparam):
        '''2.Click on image_window so send i read the message'''
        if self.drag_showing == False:
            self.showAction(self.getActionPath('click.txt'))
        else:
            self.showAction(self.getActionPath('idle.txt'))
        self.dragging = False
        self.drag_showing = False
        win32gui.ReleaseCapture()
        '''set other attaced windows' position, if put this in OnMove(), cause vanishing'''
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
        win32gui.AppendMenu(menu, win32con.MF_STRING, 5, 'auto behave')
        win32gui.AppendMenu(menu, win32con.MF_STRING, 4, 'close')
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
        return win32gui.DefWindowProc(hwnd, message, wparam, lparam)
    
    def OnSize(self, hwnd, message, wparam, lparam):
        '''
        called when window is resized.
        control things here
        '''
        return win32gui.DefWindowProc(hwnd, message, wparam, lparam)
    
    def OnPaint(self, hwnd, message, wparam, lparam):
        dc,ps = win32gui.BeginPaint(hwnd)
        if len(self.Image_list)>0:
            self.Image_list[self.image_index].draw_on_dc(dc, RGB(255,255,255))
        win32gui.EndPaint(hwnd, ps)
        return True
    
    def OnDestroy(self, hwnd, message, wparam, lparam):
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
    
    def getParentDirectory(self, path):
        return os.path.abspath(os.path.join(path, os.pardir))
        path2 = path.split('/')
        temp=''
        for ph in path2:
            if(len(ph)>4 and (ph[len(ph)-4:] == '.txt')):
                break
            temp = os.path.join(temp, ph)        
        return temp
         
    def getActionPath(self, action_filename):
        path = self.getParentDirectory(self.charFile)
        return path + '/skeleton/'+action_filename
    
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
    charFile = input('charFile=')
    win = image_window(lambda:win32gui.PostQuitMessage(0), charFile)
    win32gui.PumpMessages()

 

