import socket
import os
import threading
import time
import zipfile
import threading
import myPacket as mp
def getParentDirectory(path):
    path2 = path.split('/')
    temp=''
    for ph in path2:
        if(len(ph)>4 and (ph[len(ph)-4:] == '.txt')):
            break
        temp = os.path.join(temp, ph)        
    return temp

def checkCharVersion(sock, myChadir, friChadir):
    text = str(getCharDataSize(myChadir))
    print(text)
    mp.sendPacket(sock, text.encode('utf8'))
    data = mp.recvPacket(sock).decode('utf8')
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

def updateCharacter(sock, friChadir, friendID, func):
    fileName = friendID+'.zip'
    with open(fileName, 'wb') as cfile:
        while True:
            data = mp.recvPacket(sock)
            if data == b'EOF':
                break
            cfile.write(data)
    func(0)
    #win32gui.ShowWindow(self.hwnd, 0)
    os.system('rd /S /Q ' + friChadir)
    zf = zipfile.ZipFile(fileName)
    zf.extractall(friChadir)
    zf.close()
    func(1)
    #win32gui.ShowWindow(self.hwnd, 1)
    os.remove(fileName)

def uploadCharacter(sock, myChadir):
    sfileName = 'ArchiveName.zip'
    zf = zipfile.ZipFile(sfileName,'w',zipfile.ZIP_DEFLATED)
    for dirPath, dirNames, fileNames in os.walk(myChadir):
        for fileName in fileNames:
            file = os.path.join(dirPath, fileName)
            zf.write(file, file[len(myChadir)+1:])
    zf.close()
    with open(sfileName, 'rb') as file:
        while True:
            data = file.read(4096)
            if not data:
                break
            mp.sendPacket(sock, data)
            
    time.sleep(1) # delete after send in fixed len
    mp.sendPacket(sock, b'EOF')
    os.remove(sfileName)
    
def updataIfNeed(sock, myChafile, friendID, func, callbackFunc = None):  
    firChafile = func(None)
    friChadir = getParentDirectory(firChafile)
    myChadir = getParentDirectory(myChafile)
    if not checkCharVersion(sock, myChadir, friChadir):
        mp.sendPacket(sock, 'True'.encode('utf8'))
        data = mp.recvPacket(sock).decode('utf8')
        if data=='True':
            myThread = threading.Thread(target=uploadCharacter, args=(sock, myChadir))
            myThread.setDaemon(True)
            myThread.start()
            #uploadCharacter(sock, myChadir)
        updateCharacter(sock, friChadir, friendID, func)
    else:
        mp.sendPacket(sock, 'False'.encode('utf8'))
        data = mp.recvPacket(sock).decode()
        if data == 'True':
            uploadCharacter(sock, myChadir)
    
    myThread.join()
    sock.close()
    if callbackFunc != None:
        callbackFunc()
        
    #thread = threading.Thread(target=self.listen_to_chat_messagesInThread)
    #thread.setDaemon(True)
    #thread.start()
    #self.connected = True



    
    
