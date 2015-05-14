'''
user defined win32 message type
define new message to create main thread events
remember to add message mapping (usually set in __init__ function)
in order to catch the message (or it will be ignored)
eg: 
a thread can use win32gui.SendMessage function to send a message
that will be caught and execute in main thread (maybe for GUI purpose)
'''
import win32con
WM_CONNACCEPTED = win32con.WM_APP+1
WM_CHATMSGRECV = win32con.WM_APP+2
WM_FRIENDREFRESHED = win32con.WM_APP+3
