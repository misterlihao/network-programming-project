import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.constants import HORIZONTAL
import mailHandle as mh
import friend_window as fw

class SendMailWindow:
    def __init__(self, sender_mail,  recipient_mail, pwd):
        '''
        create the add friend window.
        '''
        self.root = tk.Tk()
        self.root.title('Send email to '+recipient_mail)
        
        self.sender_mail = sender_mail
        self.recipient_mail = recipient_mail
        self.password = pwd
        self.pane_for_recipient = tk.PanedWindow(self.root,orient=tk.HORIZONTAL, borderwidth=5)
        self.pane_for_recipient.pack(fill=tk.BOTH)
        self.lable_for_recipient = tk.Label(self.pane_for_recipient, text='To:', width=5, justify=tk.LEFT, anchor=tk.W)
        self.entry_for_recipient = tk.Entry(self.pane_for_recipient, width=10)
        self.entry_for_recipient.insert(0, recipient_mail)
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
        
        self.root.geometry('300x200')
        
    def SendMail(self):
        sender = self.sender_mail
        password = self.password
        recipient_email = self.entry_for_recipient.get()
        topic = self.entry_for_topic.get()
        text = self.text_for_content.get(1.0, tk.END)
        '''call www's function here'''
        myEmail = mh.Email(sender, password)
        if myEmail.login()!=True:
            fw.OpenLogInWindow(self)
        else:
            myEmail.sendMailSmtp(recipient_email, topic, text)
            '''close after send'''
            self.Destroy()
            print('Sender: ',sender, '\nTo: ', recipient_email, '\nTopic: ', topic)
            print('Text: \n', text)
        
    def Destroy(self):
        self.root.destroy() 
        
if __name__=='__main__':
    mySMW = SendMailWindow('DefaultSender@gmail.com', 'DefaultReceiver', 'DefaultReceiver@gmail.com', 'defaultPassword')
    mySMW.root.mainloop()