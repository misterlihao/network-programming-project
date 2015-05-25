from online_check import *
class FriendList:
    '''
    form of items = [ip, name, status, id, email]
        '''
    def __init__(self, file_name):
        self.file_name = file_name
        self.ip_name_status_list = []
        self.id_max = 0
        with open(self.file_name) as file:
            for line in file:
                if line[-1]=='\n':
                    line = line[:-1]
                ip, name,id,email = line.split(':')
                self.ip_name_status_list.append([ip, name, False, id, email])#default to offline
                if int(self.id_max) < int(id):
                    self.id_max = int(id)
                
    def Save(self):
        with open(self.file_name, 'w') as file:
            for each in self.ip_name_status_list:
                file.write('%s:%s:%s:%s\n'%(each[0],each[1],each[3], each[4]))
    
    def ChangeFriendName(self, friend_id, new_name):
        for list in self.ip_name_status_list:
            if (list[3]==friend_id):
                list[1] = new_name;
                break;
    
    def ChangeFriendIp(self, friend_id, new_ip):
        for list in self.ip_name_status_list:
            if (list[3]==friend_id):
                list[0] = new_ip;
                break;
            
    def ChangeFriendEmail(self, friend_id, new_email):
        for list in self.ip_name_status_list:
            if (list[3]==friend_id):
                list[4] = new_email
                break;
        
    def RefreshOnlineStatus(self):
        '''
        refresh online status
        '''
        updated_friends = []
        for each in self.ip_name_status_list:
            if CheckSomeoneOnline(each[0]) == True\
                    and each[2] == False:
                updated_friends.append(self.ip_name_status_list.index(each))
                each[2] = True
            elif CheckSomeoneOnline(each[0]) == False\
                    and each[2] == True:
                updated_friends.append(self.ip_name_status_list.index(each))
                each[2] = False
        return updated_friends
    
    def AddNewFriend(self,ip, name, email):
        '''
        '''
        self.ip_name_status_list.append([ip, name, False, self.id_max+1], email)
        self.id_max += 1
        pass
    
    def __len__(self):
        return len(self.ip_name_status_list)
    
    def __getitem__(self, arg):
        return self.ip_name_status_list[arg]
        
    def __iter__(self):
        '''
        iteration of [ip, name, status, id]
        '''
        for item in self.ip_name_status_list:
            yield item