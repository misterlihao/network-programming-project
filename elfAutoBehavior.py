import random, time, threading, ctypes, win32gui

class ElfAutoBehavior(threading.Thread):
    
    def __init__(self, imageWin, actionList=[]):
        self.moveWindow = imageWin.MoveTo
        self.showAction = imageWin.showAction
        self.getActionPath = imageWin.getActionPath
        self.actionList = actionList
        self.imageWin = imageWin
        self.setCoordinate()
        self.isWalk = False
        self.isAction = False
        user32 = ctypes.windll.user32
        self.screenSize = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
        super(ElfAutoBehavior, self).__init__()

    def setCoordinate(self):
        left, top, right, bottom = win32gui.GetWindowRect(self.imageWin.hwnd)
        self.coordinate = [left, top]
        
    def walk(self, x, y, n):
        for i in range(n):
            if not self.isAction:
                self.setCoordinate()
                self.coordinate[0] += x
                self.coordinate[1] += y
                
                if self.coordinate[0] < 0:
                    self.coordinate[0] = self.screenSize[0]-150
                elif self.coordinate[0]+100 > self.screenSize[0]:
                    self.coordinate[0] = 0
                if self.coordinate[1] < 0:
                    self.coordinate[1] = self.screenSize[1]-150
                elif self.coordinate[1]+100 > self.screenSize[1]:
                    self.coordinate[1] = 0
    
                self.moveWindow(self.coordinate[0], self.coordinate[1])
                time.sleep(0.3)
            else:
                break
        return
    
    def check(self):
        self.imageWin.actionThread.join()
        if self.isWalk:
            self.isAction = True
        return

    def action(self, name):
        self.showAction(self.getActionPath(name), False)
        
    def run(self):
        distance = 5
        time.sleep(5)
        while True:
            while self.imageWin.autoBehave == False:
                time.sleep(2)
            x = random.randint(-1, 1) * distance
            y = random.randint(-1, 1) * distance    
            if x == 0 and y == 0:
                x = -1
            if self.isAction:
                if self.imageWin.actionNow == 'idle.txt':
                    self.isAction = False
                else:
                    time.sleep(5)
                    continue
            self.isWalk = True
            self.showAction(self.getActionPath(self.actionList[0]), True) 
            checkThread = threading.Thread(target=self.check)
            checkThread.setDaemon(True)
            checkThread.start()
            self.walk(x,y,10)
            self.isWalk = False
            if self.isAction:
                time.sleep(5)
                continue
            
            actionIndex = random.randint(1, len(self.actionList)-1)
            self.action(self.actionList[actionIndex])
            myThread = self.imageWin.actionThread
            while True:
                if myThread.is_alive():
                    if myThread.only_once:
                        myThread.join()
                        break
            
        