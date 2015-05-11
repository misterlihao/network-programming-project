'''
'''
import socket
import sys
import select
import threading

RECVMAXLEN=1000

def wait_for_message(sock_list, timeout=-1) :
    '''
    Block until any message, return (message, index)
    .RECVMAXLEN=Bytes to set recv length
    '''
    if timeout == -1:
        readable = select.select(sock_list,[],[])[0]
    return readable[0].recv(RECVMAXLEN), sock_list.index(readable[0])

