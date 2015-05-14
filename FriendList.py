from online_check import *
class FriendList:
    def __init__(self, file_name):
        self.file_name = file_name
        self.ip_name_status_list = []
        with open(self.file_name) as file:
            for line in file:
                ip, name = line.split(':')
                if name[-1]=='\n':
                    name = name[:-1]
                self.ip_name_status_list.append([ip, name, 'Off'])#default to offline
                
    def Save(self):
        with open(self.file_name, 'w') as file:
            for each in self.ip_name_status_list:
                file.write(each[0]+':'+each[1]+'\n')
    
    def ChangeFriendName(self, friend_name, new_name):
        for list in self.ip_name_status_list:
            if (list[1]==friend_name):
                list[1] = new_name;
                print("changed name to %s" % new_name)      
                break;
    
    def ChangeFriendIp(self, friend_name, new_ip):
        for list in self.ip_name_status_list:
            if (list[1]==friend_name):
                list[0] = new_ip;
                print("changed ip to %s" % new_ip)
                break;
        
    def RefreshOnlineStatus(self):
        '''
        refresh online status
        '''
        updated_friends = []
        for each in self.ip_name_status_list:
            if CheckSomeoneOnline(each[0]) == True\
                    and each[2] == 'Off':
                updated_friends.append(self.ip_name_status_list.index(each))
                each[2] = 'On'
            elif CheckSomeoneOnline(each[0]) == False\
                    and each[2] == 'On':
                updated_friends.append(self.ip_name_status_list.index(each))
                each[2] = 'Off'
        
        return updated_friends
    
    def AddNewFriend(self,ip, name):
        '''
        '''
        self.ip_name_status_list.append([ip, name, 'Off'])
        
        pass
    
    def __len__(self):
        return len(self.ip_name_status_list)
    
    def __getitem__(self, arg):
        return self.ip_name_status_list[arg]
        
    def __iter__(self):
        '''
        iteration of [ip, name, status]
        '''
        for item in self.ip_name_status_list:
            yield item