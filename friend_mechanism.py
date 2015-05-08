import sys

def ReadFriendList(file_name):
    friends_status_list = []
    with open(file_name) as file:
        for line in file:
            ip, name = line.split(':')
            friends_status_list.append((ip, name, 'Off'))#default to offline
            print(friends_status_list)
        return friends_status_list
            
def WriteFriendList(file_name, friends_status_list):
    with open(file_name, 'w') as file:
        for each in friends_status_list:
            file.write(each[0]+':'+each[1])
            
def RefreshOnlineFriends(friends_status_list):
    for each in friends_status_list:
        if CheckSomeoneOnline(each[0]) == True:
            refreshed_list.append((each[0], each[1], 'On'))
        elif CheckSomeoneOnline(each[0]) == False:
            refreshed_list.append((each[0], each[1], 'Off'))
    return refreshed_list

def AddNewFriend(friends_status_list, ip, name):
    friends_status_list.append((ip, name, 'Off'))
    RefreshOnlineFriends(friends_status_list)
    pass