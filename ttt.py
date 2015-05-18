import zipfile, os

sfileName = 'ArchiveName.zip'

ch = 'data/cha/character1/character1.txt'
pch = 'data/cha/character1'
zf = zipfile.ZipFile(sfileName,'w',zipfile.ZIP_DEFLATED)
for dirPath, dirNames, fileNames in os.walk(pch):
    for fileName in fileNames:
        file = os.path.join(dirPath, fileName)
        zf.write(file, file[len(pch)+1:])
zf.close()

def getParentDirectory(path):
        #return os.path.abspath(os.path.join(path, os.pardir))
    path2 = path.split('/')
    temp=''
    for ph in path2:
        if(len(ph)>4 and (ph[len(ph)-4:] == '.txt')):
            break
        temp = os.path.join(temp, ph)         
    return temp


print(getParentDirectory(ch))
