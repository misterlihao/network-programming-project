import socket
import os
import time

def getParentDirectory(path):
    path2 = path.split('/')
    temp=''
    for ph in path2:
        if(len(ph)>4 and (ph[len(ph)-4:] == '.txt')):
            break
        temp = os.path.join(temp, ph)        
    return temp

def checkCharVersion(sock, myChafile, friChadir):
    print('check Character ...')
    text = str(getCharDataSize(getParentDirectory(myChafile)))
    #print('character1=' + text)
    sock.send(text.encode('utf8'))
    data = sock.recv(8192).decode('utf8')
    if cmpCharVersion(getCharDataSize(friChadir), int(data)):
        return True
    return False


def cmpCharVersion(myDataSize = 0, hisDataSize = 0):
    if myDataSize == hisDataSize:
        return True
    return False

def getCharDataSize(charDirectory):
    temp = 0
    for dirPath, dirNames, fileNames in os.walk(charDirectory):
        for fileName in fileNames:
            file = os.path.join(dirPath, fileName)
            temp += os.path.getsize(file)
    return temp

def updateCharacter(friChadir, friendID, func):
    print('update Character ...')
    fileName = friendID+'.zip'
    with open(fileName, 'wb') as cfile:
        while True:
            data = sock.recv(4096)
            if data == b'EOF':
                print('recv file success!')
                break
            cfile.write(data)
    func(0)
    #win32gui.ShowWindow(self.hwnd, 0)
    os.system('rd /S /Q ' + friChadir)
    zf = zipfile.ZipFile(fileName)
    zf.extractall(friChadir)
    print('update success')
    zf.close()
    func(1)
    #win32gui.ShowWindow(self.hwnd, 1)
    os.remove(fileName)

def uploadCharacter(myChafile):
    print('upload Character ...')
    sfileName = 'ArchiveName.zip'
    zf = zipfile.ZipFile(sfileName,'w',zipfile.ZIP_DEFLATED)
    parentDir = getParentDirectory(myChafile)
    #print(parentDir)
    for dirPath, dirNames, fileNames in os.walk(parentDir):
        for fileName in fileNames:
            file = os.path.join(dirPath, fileName)
            #print(file)
            zf.write(file, file[len(parentDir)+1:])
    zf.close()
    with open(sfileName, 'rb') as file:
        while True:
            data = file.read(4096)
            if not data:
                break
            sock.send(data)
            
    time.sleep(1) # delete after send in fixed len
    sock.send(b'EOF')
    print('send success!')
    os.remove(sfileName)
    
def updataIfNeed(sock, myChafile, friendID, func, callbackFunc = None):  
    if not checkCharVersion():
        sock.send('True'.encode('utf8'))
        data = self.sock.recv(8192).decode()
        if data=='True':
            uploadCharacter(myChafile)
        friChadir = 'data/cha/' + str(friendID)
        updateCharacter(friChadir, friendID, func)
    else:
        sock.send('False'.encode('utf8'))
        data = sock.recv(8192).decode()
        if data == 'True':
            uploadCharacter(myChafile)
    if callbackFunc != None:
        callbackFunc()
        
    #thread = threading.Thread(target=self.listen_to_chat_messagesInThread)
    #thread.setDaemon(True)
    #thread.start()
    #self.connected = True



    
    
