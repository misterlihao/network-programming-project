import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.constants import HORIZONTAL
import SendMailWindow as smw

'''parameters'''
'''sender:string of mail from who'''
'''topic:string of mail's topic'''
'''text:string of mail's text'''
class ReadMailWindow:
    def __init__(self, receiver='DefaultMe@gmail.com', sender='DefaultUser@gmail.com', topic='DefaultTopic', text='Dear:\n\nDefaultLine\nDefaultLine2\nDefaultLine3\n\nSincerely,\nDefaultUser'):
        '''
        create the ReadMailWindow.
        '''
        self.root = tk.Tk()
        self.root.title('Mail from '+sender)
        self.root.geometry('300x200')
        
        self.receiver=receiver
        self.sender=sender
        self.topic=topic
        self.text=text
        
        self.pane_for_sender = tk.PanedWindow(self.root,orient=tk.HORIZONTAL, borderwidth=5)
        self.pane_for_sender.pack(fill=tk.BOTH)
        self.lable_for_sender = tk.Label(self.pane_for_sender, text='From:', width=5, justify=tk.LEFT, anchor=tk.W)
        self.entry_for_sender = tk.Entry(self.pane_for_sender, width=10)
        self.entry_for_sender.insert(0, self.sender)
        self.entry_for_sender.config(state=tk.DISABLED)
        self.pane_for_sender.add(self.lable_for_sender)
        self.pane_for_sender.add(self.entry_for_sender)
        
        self.pane_for_topic = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, borderwidth=5)
        self.pane_for_topic.pack(fill=tk.BOTH)
        self.lable_for_topic = tk.Label(self.pane_for_topic, text='Topic:', width=5, justify=tk.LEFT, anchor=tk.W)
        self.entry_for_topic = tk.Entry(self.pane_for_topic, width=10)
        self.entry_for_topic.insert(0, self.topic)
        self.entry_for_topic.config(state=tk.DISABLED)
        self.pane_for_topic.add(self.lable_for_topic)
        self.pane_for_topic.add(self.entry_for_topic)
        
        self.pane_for_content = tk.PanedWindow(self.root, orient=HORIZONTAL, borderwidth=7)
        self.pane_for_content.pack(fill=tk.BOTH, expand=1)
        self.lable_for_content = tk.Label(self.pane_for_content, text='Text:', justify=tk.LEFT, anchor=tk.W)
        self.text_for_content = ScrolledText(self.pane_for_content, width=10, height=4)
        self.text_for_content.insert(1.0, self.text)
        self.text_for_content.config(state=tk.DISABLED)
        self.pane_for_content.add(self.lable_for_content)
        self.pane_for_content.add(self.text_for_content)
        
        self.pane_for_button = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.pane_for_button.pack(fill=tk.BOTH)
        self.button_for_reply = tk.Button(self.pane_for_button, text="Reply", command=self.Reply)
        self.button_for_close = tk.Button(self.pane_for_button, text="Exit", command=self.Destroy, width=5)
        self.pane_for_button.add(self.button_for_close) 
        self.pane_for_button.add(self.button_for_reply)
        

    def Reply(self):
        self.SMW = smw.SendMailWindow(self.receiver, self.sender, self.friend_window.email_passwd)
        self.SMW.text_for_content.insert(1.0, '\n\n---------------\n'+self.text)
        #self.root.destroy()
    
    def Destroy(self):
        self.root.destroy() 
        
if __name__=='__main__':
    myRMW = ReadMailWindow()
    myRMW.root.mainloop()