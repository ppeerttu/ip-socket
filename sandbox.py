# -*- coding: utf-8 -*-

import socket

class udpsocket:
    'Used for sending UDP datagrams'

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = sock


class tcpsocket:
    'Used for the first transmission via TCP'

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host,port))

    def send(self, msg):
        self.socket.send(msg)

    def myreceive(self):
        chunk = ws.recv(2048)
        if chunk == '':
            print "Message ended"
            break;
        chunks.append(chunk)
        print ("Received ", chunks)
        




address = "ii.virtues.fi"
port = 10000

try:
    ws.connect((address, port))
    print "Connection successfull"
    sent =  ws.send("HELLO\r\n")
    print (sent, " bytes sent")
    
    chunks = []
    while True:
        chunk = ws.recv(2048)
        if chunk == '':
            print "Message ended"
            break;
        chunks.append(chunk)
        print "Something received"
    
    print (chunks)
except Exception as e:
    print "Somethin's wrong with %s:%d. Exception is %s" % (address, port, e)

finally:
    print "Closing..."
    ws.close()
