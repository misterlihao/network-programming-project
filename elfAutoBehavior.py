import random, time, threading



class ElfAutoBehavior(threading.Thread):
    
    def __init__(self, imageWin, actionList=[]):
        self.moveWindow = imageWin.MoveTo
        self.showAction = imageWin.showAction
        self.getActionPath = imageWin.getActionPath
        self.actionList = actionList
        self.imageWin = imageWin

    def walk(self, x, y, n):
        for i in range(n):
            self.showAction(self.getActionPath(name), True)
            self.moveWindow(x, y)
            time.sleep(1)
            
    def action(self, name):
        self.showAction(self.getActionPath(name), False)
        
    def run(self):
        distance = 10
        while True:
            x = random.randint(0, 2) * distance
            y = random.randint(0, 2) * distance     
            self.walk(x, y, 10)
            actionIndex = random.randint(1, len(self.actionList))
            self.action(self.actionList[actionIndex])
            myThread = self.imageWin.actionThread
            while True:
                if myThread.is_alive():
                    if myThread.only_once:
                        myThread.join()
                        break
            
        