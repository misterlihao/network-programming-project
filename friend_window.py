'''
@author: misterlihao
This is supposed to be main window
'''
from image_window import image_window
import win32gui
import time
import threading
import Image

def func():
    global win
    while True:
        time.sleep(0.15)
        win.SwitchNextImage()
    
def after_window_closed():
    win32gui.PostQuitMessage(0)

def create_image_window(character_path):
    pass
if __name__ == '__main__':
    win = image_window(after_window_closed)
    win.CreateWindow()
    win.Resize(256, 128)
    hbmp1 = win32gui.LoadImage(0, 'shime1.bmp', win32gui.IMAGE_BITMAP, 0, 0,win32gui.LR_LOADFROMFILE)
    hbmp2 = win32gui.LoadImage(0, 'shime2.bmp', win32gui.IMAGE_BITMAP, 0, 0,win32gui.LR_LOADFROMFILE)
    hbmp3 = win32gui.LoadImage(0, 'shime3.bmp', win32gui.IMAGE_BITMAP, 0, 0,win32gui.LR_LOADFROMFILE)
    img1 = Image.Image()
    img1.append_component(hbmp1, 0, 0, 128, 128)
    img1.append_component(hbmp2, 128, 0, 128, 128)
    img2 = Image.Image()
    img2.append_component(hbmp2, 0, 0, 128, 128)
    img2.append_component(hbmp3, 128, 0, 128, 128)
    img3 = Image.Image()
    img3.append_component(hbmp3, 0, 0, 128, 128)
    img3.append_component(hbmp1, 128, 0, 128, 128)
    
    win.SetImages([img1, img2, img3])
    win.SwitchNextImage()
    threading.Thread(target = func).start()
    win32gui.PumpMessages()
    print('end')