from online_check import *
class FriendList:
    def __init__(self, file_name):
        self.file_name = file_name
        self.friends_status_list = []
        with open(self.file_name) as file:
            for line in file:
                ip, name = line.split(':')
                self.friends_status_list.append([ip, name, 'Off'])#default to offline
                
    def Save(self):
        with open(self.file_name, 'w') as file:
            for each in self.friends_status_list:
                file.write(each[0]+':'+each[1])
        
    def RefreshOnlineStatus(self):
        '''
        refresh online status
        '''
        for each in self.friends_status_list:
            if CheckSomeoneOnline(each[0]) == True:
                each[2] = 'On'
            elif CheckSomeoneOnline(each[0]) == False:
                each[2] = 'Off'

    def AddNewFriend(self,ip, name):
        '''
        '''
        self.friends_status_list.append([ip, name, 'Off'])
        
        pass