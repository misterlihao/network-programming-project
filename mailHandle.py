import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import sys
import email, email.header
import email.charset
import xml.etree.ElementTree
#import re

class Email:

    def __init__(self, account, password, friends=[]):
        self.account = account
        self.password = password
        self.sHost, self.sPort, self.iHost, self.iPort = self.getServer()       
        self.friends = friends
        
        self.isLogin = True
        #self.isLogin = False
        #self.login()
        
    def login(self, account=None, password=None):
        if account:
            self.account = account
        if password:
            self.password = password
        self.sHost, self.sPort, self.iHost, self.iPort = self.getServer()
        try:
            mailServer = smtplib.SMTP_SSL(self.sHost, self.sPort)
            mailServer.set_debuglevel(1)
            mailServer.login(self.account, self.password)
            self.isLogin = True
            return True
        except:
            self.isLogin = False
            return False
    
    def getServer(self):
        temp = self.account.split('@', 1)
        temp = temp[1].split('.')[0]
        if temp == 'gmail':
            return 'smtp.gmail.com', 465, 'imap.gmail.com', 993
        elif temp == 'yahoo':
            return 'smtp.mail.yahoo.com', 465, 'imap.mail.yahoo.com', 993
        return 'undefined'
        

    def sendMailSmtp(self, recipient, subject, content, first=False):
        if self.isLogin or first:
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
        if self.isLogin:
            if len(self.friends) > 0:
                imapServer = imaplib.IMAP4_SSL(self.iHost, self.iPort)
                imapServer.login(self.account, self.password)
                imapServer.select()
     
                for friend in self.friends:
                    mailDict[friend] = []
                    criterionFrom = '(FROM ' + '\"' + friend + '\")'
                    #print(criterionFrom)
                    typ, msgnums = imapServer.search(None, criterionFrom, 'UNSEEN')
                
                    for num in msgnums[0].split():
                        typ, data = imapServer.fetch(num, '(RFC822)')
                        mailDict[friend].append(self.parsingMail(data[0][1]))
                #typ, msgnums = imapServer.search(None, '(FROM "pe83aa517z@gmail.com")')
                #typ, msgnums = imapServer.search(None, '(FROM "pe83aa517z@gmail.com")', 'UNSEEN')
                #typ, msgnums = imapServer.search(None, 'ALL')

                    
                imapServer.close()
                imapServer.logout()
                return mailDict
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
        #print(mailContent)
        return (strFrom, strSubject, mailContent, message['Date'], suffix)
    
    def remove_tags(self, text):
        return ''.join(xml.etree.ElementTree.fromstring(text).itertext())
        #TAG_RE = re.compile(r'<[^>]+>')
        #return TAG_RE.sub('', text)
        
if __name__  == '__main__':

    account = 'bbai14915@gmail.com'
    password = 'zxc09876'
    recipient = 'pe83aa517z@gmail.com'
    subject = 'test python'
    content = 'YAPYAPYAP22'
    friends = ['pe83aa517z@gmail.com', 'pe83aa517z@yahoo.com.tw']
    print('Start...')
    e = Email(account, password, friends)
    #e.login(account, password)
    #e.login()
    #e.sendMailSmtp(recipient, subject, content)
    mailDict = e.getEmail()
    
    for list in mailDict.keys():
        for mess in mailDict[list]:
            for string in mess:
                print(string)
        print() 
    print('end')

    
