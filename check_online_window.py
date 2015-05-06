import tkinter as tk
import tkinter.messagebox as tkmb
from online_check import CheckSomeoneOnline

class open_check_online_window():
    def __init__(self, x, y):
        self.co = tk.Tk()
        self.co.title('enter ip to check')
        self.co.resizable(False, False)
        self.co.wm_attributes("-toolwindow", 1)
        self.entry = tk.Entry(self.co, width=15)
        self.entry.pack(side = 'left', fill = 'both')
        check = tk.Button(self.co,
                          text='check',
                          relief = 'flat',
                          command=self.check_online)
        check.pack(side = 'right', fill = 'both')
        self.co.geometry('+%d+%d'% (x,y))
        self.co.mainloop()
        
    def on_return(self, event):
        self.check_online()
        
    def check_online(self):
        ip = self.entry.get()
        try:
            if CheckSomeoneOnline(ip) == True:
                print(ip)
                tkmb.showinfo('online check', ip+'is online')
            else:
                tkmb.showinfo('online check', ip+'is offline')
        except Exception as err:
            tkmb.showerror('Error', err)
        self.co.quit()
    
if __name__ == '__main__':
    open_check_online_window(600, 300)