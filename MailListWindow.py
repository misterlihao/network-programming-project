import tkinter as tk
from tkinter import Toplevel

class MailListWindow:
    def __init__(self, title):
        self.win = Toplevel()
        self.win.title(title)
        self.win.geometry('400x200')
        self.win.wm_attributes('-toolwindow', True)
        
        canvas = tk.Canvas(self.win, background='white')
        scrollbar = tk.Scrollbar(self.win,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=1)
        
        inner_frame = tk.Frame(canvas)
        self.frame_id = canvas.create_window((0,0),window=inner_frame, anchor='nw')
        inner_frame.bind('<Configure>', self.onFrameConfigure)
        canvas.bind('<Configure>', self.onCanvasConfigure)
        
        self.frame = inner_frame
        self.canvas = canvas
        
    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def onCanvasConfigure(self, event):
        self.canvas.itemconfig(self.frame_id, width=event.width-2)
    
    def insertButton(self, text, callback):
        btn = tk.Button(self.frame, bg='#fafafa',text=text, command=callback)
        btn.pack(fill='both', expand=1)
    
    def callback(self):
        print('click')
    
if __name__ == '__main__':
    root = tk.Tk()
    mlw = MailListWindow('mail "xxx"')
    mlw.insertButton('hahaha', None)
    mlw.insertButton('hahaha', None)
    mlw.insertButton('hahaha', None)
    mlw.insertButton('hahaha', None)
    mlw.insertButton('hahaha', None)
    root.wm_withdraw()
    root.mainloop()
    