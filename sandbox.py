# -*- coding: utf-8 -*-

import socket
import struct

class UdpSocket:
    'Used for sending UDP datagrams'

    # Constructor - this function initializes the socket object
    def __init__(self, cid, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = sock
        self.cid = cid

    # This function is propably no needed since the udp socket can receive datagrams without binding
    def bind(self, host, port):
        self.sock.bind((host, port))

    # This function sends the message it gets as a parameter to ii.virtues.fi:23432
    # However, static receiver must be replaced with dynamic receiver i.e. in __init__ function
    def send(self, message):
        
        # Calculate the length of the actual message in bytes
        length = len(message)
        
        # Add null characters until the full length of the message is 64 bytes
        for n in range(64 - length):
            message += '\0'
        
        # Udp headers - when adding features, all of these three must be modified regarding the state of the communication
        ack = True
        eom = False
        remaining = 0

        # Pack the data into raw format and send it to the receiver
        data = struct.pack('!8s??HH64s', cid, ack, eom, remaining, length, message)
        self.sock.sendto(data, ("ii.virtues.fi", 23432))

    def receive(self):
        # Listen to socket max 2048 bytes - this should propably be implemented in better way later
        data = self.sock.recvfrom(2048)

        # Unpack the raw data into understantable form
        try:
            print data
            cid, ack, eom, remaining, length, message = struct.unpack('!8s??HH64s', data)
        except Exception as e:
            print e
        

class TcpSocket:
    'Used for the first transmission via TCP'

    # Constructor - this function initializes the socket object
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    # This function sets up the connection - you need to call this in order to send or receive anything
    def connect(self, host, port):
        self.sock.connect((host,port))

    # This function sends blindly (no validation) message to the receiver
    def send(self, msg):
        self.sock.send(msg)

    # This function receives blindly (max 2048 bytes) message
    def receive(self):
        chunk = self.sock.recv(2048)
        return chunk            

    # This function closes the TCP connection
    # However, we should investigate whether this is enough for proper closing of TCP connection
    def close(self):
        self.sock.close()



############################### APPLICATION LOGIC
############################### Add functions used in main right below this
############################### so that they are introduced before actually used

address = "ii.virtues.fi"
tcpPort = 10000

tsocket = TcpSocket()




tsocket.connect(address, tcpPort)
tsocket.send("HELLO\r\n")
received = tsocket.receive()
print "Received: ", received
msg, cid, udpPort = received.split()
print msg
print cid
print udpPort

usocket = UdpSocket(cid)

try:
    hellomsg = "Hello from "
    hellomsg += cid
    print "Hellomessage: ", hellomsg
    usocket.send(hellomsg)
    usocket.receive()
except Exception as e:
    print "Something is wrong with your class: ", e

finally:
    tsocket.close()
    print "Closing..."
    
