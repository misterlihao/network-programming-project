'''
mailHandle

mailHandle.Email(account[, password][, friends])
    account and password are string(users email account and password)
    friends is List
    
mailHandle.setFriends([friends])
    friends is List with value string(friend name)
    set users friends which want to getEmail()  
    
mailHandle.login([account[, password]])
    account and password are string(users email account and password)
    should use login() and Success before sendMailSmtp() and getEmail(), 
    Otherwise it will not be executed
    it will return Boolean to tell Login status

mailHandle.sendMailSmtp(recipient, subject, content)
    recipient, subject and content are string
    recipient is email recipient
    subject is email subject
    content is email content
    it will return Boolean to tell successful or not
    
mailHandke.getEmail()
    it will return dictionary with keys are friend and value is a List
    the one of List value  is a email data
    the data is a tuple (strFrom, strSubject, strContent, strDate, strsSuffix)
    it will return None if connection error
    
    
'''
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import sys
import email, email.header
import email.charset
import xml.etree.ElementTree

class Email:

    def __init__(self, account='', password='', friends=[]):
        self.account = account
        self.password = password
        if account != '':
            self.sHost, self.sPort, self.iHost, self.iPort = self.getServer()       
        self.friends = friends
        
        self.isLogin = False
        
    def setFriends(self, friends=[]):
        self.friends = friends
        
    def login(self, account=None, password=None):
        if account:
            self.account = account
        if password:
            self.password = password
        self.sHost, self.sPort, self.iHost, self.iPort = self.getServer()
        try:
            mailServer = smtplib.SMTP_SSL(self.sHost, self.sPort)
            mailServer.set_debuglevel(0)
            mailServer.login(self.account, self.password)
            self.isLogin = True
            return True
        except:
            self.isLogin = False
            return False
    
    def getServer(self):
        temp = self.account.split('@', 1)
        if len(temp) != 1:
            temp = temp[1].split('.')[0]
            if temp == 'gmail':
                return 'smtp.gmail.com', 465, 'imap.gmail.com', 993
            elif temp == 'yahoo':
                return 'smtp.mail.yahoo.com', 465, 'imap.mail.yahoo.com', 993
        return 'undefined', 0, '', 0
        

    def sendMailSmtp(self, recipient, subject, content):
        if self.isLogin:
            message = MIMEMultipart()
            message['From'] = self.account
            message['To'] = recipient
            message['Subject'] = subject
            message.attach(MIMEText(content))
            mailServer = smtplib.SMTP_SSL(self.sHost, self.sPort)
            mailServer.set_debuglevel(1)
            mailServer.login(self.account, self.password)
            mailServer.sendmail(self.account, recipient, message.as_string())
            mailServer.close()
            return True
        return False
    
    def getEmail(self):
        mailDict = {}
        try:
            if self.isLogin:
                if len(self.friends) > 0:
                    imapServer = imaplib.IMAP4_SSL(self.iHost, self.iPort)
                    imapServer.login(self.account, self.password)
                    imapServer.select()
         
                    for friend in self.friends:
                        #mailDict[friend] = []
                        criterionFrom = '(FROM ' + '\"' + friend + '\")'
                        typ, msgnums = imapServer.search(None, criterionFrom, 'UNSEEN')
                        #typ, msgnums = imapServer.search(None, criterionFrom)
                        isfirst=True
                        for num in msgnums[0].split():
                            typ, data = imapServer.fetch(num, '(RFC822)')
                            if isfirst:
                                isfirst = False
                                mailDict[friend] = []
                            mailDict[friend].append(self.parsingMail(data[0][1]))
    
    
                        
                    imapServer.close()
                    imapServer.logout()
                    return mailDict
        except:
            print('getEmail error')
            return None
        return mailDict
    
    def unicode(self, text, encoding=None):
        if encoding == None:
            return text
        return text.decode(encoding)
    
    
    def parsingMail(self, data):
        message = email.message_from_bytes(data, _class=email.message.Message)
        
        temp = message['From'].split(' ')
        if len(temp) == 2:
            fromname = email.header.decode_header(temp[0].strip('\\'))
            strFrom = self.unicode(fromname[0][0], fromname[0][1]) +' '+ temp[1]
        else:
            strFrom = message['From']
            
        subject = email.header.decode_header(message['Subject'])
        strSubject = self.unicode(subject[0][0], subject[0][1])
        
        mailContent = ''
        contenttype = None
        suffix = '' 
        for part in message.walk():
            if not part.is_multipart():
                contenttype = part.get_content_type()
                filename = part.get_filename()
                charset = part.get_content_charset()
                if filename:     #is annex?
                    print(filename)
                else:
                    if charset == None:
                        mailContent = part.get_payload()
                    else:
                        mailContent = part.get_payload(decode=True).decode(charset)
                    if contenttype in ['text/plain']:
                        suffix = '.txt'
                    elif contenttype in ['text/html']:
                        suffix = '.htm'
                        mailContent = self.remove_tags(mailContent)
        return (strFrom, strSubject, mailContent, message['Date'], suffix)
    
    def remove_tags(self, text):
        return ''.join(xml.etree.ElementTree.fromstring(text).itertext())

        
if __name__  == '__main__':

    #account = 'bbai14915@gmail.com'

    account = 'bbai1gmail.com'
    password = 'zxc09876'
    recipient = 'pe83aa517z@gmail.com'
    subject = 'test python'
    content = 'YAPYAPYAP22\n'
    friends = ['pe83aa517z@gmail.com', 'pe83aa517z@yahoo.com.tw']
    print('Start...')
    #e = Email(account, password, friends)
    e = Email()
    print(str(e.login(account, password)))
    #e.login()
    e.sendMailSmtp(recipient, subject, content)
    e.setFriends(friends)
    mailDict = e.getEmail()
    
    for list in mailDict.keys():
        for mess in mailDict[list]:
            for string in mess:
                print(string)
        print()
    print('end')

    
