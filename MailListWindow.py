import tkinter as tk
from tkinter import Toplevel

class MailListWindow:
    def __init__(self, title):
        self.win = Toplevel()
        self.win.title(title)
        self.win.geometry('400x200')
        self.win.wm_attributes('-toolwindow', True)
        
        inner_frame = tk.Frame(self.win)#inner_frame = tk.Frame(canvas)
        inner_frame.pack(side='left', fill='both', expand = 1)
        scrollbar = tk.Scrollbar(self.win,orient="vertical",command=self.scrolly)
        scrollbar.pack(side='right', fill='y')
        
        self.btn_count = 0
        self.btns = []
        self.texts = []
        self.callbacks = []
        self.frame = inner_frame
        self.scrollbar = scrollbar
        self.btn_per_page = 4
        self.first_btn = 0
        self.scrolly('', '0.0')
        
    def scrolly(self, cmd, pos, what=''):
        if self.btn_per_page <= self.btn_count:
            bar_len = self.btn_per_page/self.btn_count
        else:
            bar_len=1
        self.first_btn = int(float(pos)*self.btn_count)
        pos = str(self.getScrollPos())
        self.scrollbar.set(pos, str(float(pos)+bar_len))
        for i in range(len(self.btns)):
            mail_index = i+self.first_btn
            self.btns[i].config(text=self.texts[mail_index], command=self.callbacks[mail_index])
    
    def insertButton(self, text, callback):
        if self.btn_count < self.btn_per_page:
            btn = tk.Button(self.frame, bg='#fafafa',text=text, command=callback)
            btn.pack(fill='both', expand=1)
            self.btns.append(btn)
            
        self.btn_count += 1
        self.texts.append(text) 
        self.callbacks.append(callback)
        self.scrolly('', self.getScrollPos())
        
    def getScrollPos(self):
        if self.btn_per_page >= self.btn_count:
            return 0.0
        if self.btn_count == 0:
            return 0.0
        return self.first_btn/self.btn_count
        
    def callback(self):
        print('click')
    
if __name__ == '__main__':
    root = tk.Tk()
    mlw = MailListWindow('mail "xxx"')
    mlw.insertButton('1'*10, None)
    mlw.insertButton('2'*10, None)
    root.wm_withdraw()
    root.mainloop()
    