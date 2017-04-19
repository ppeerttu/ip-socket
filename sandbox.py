# -*- coding: utf-8 -*-

import socket
import struct

class UdpSocket:
    'Used for sending UDP datagrams'

    # Constructor - this method initializes the socket object
    def __init__(self, cid, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = sock
        self.cid = cid

    # This method is propably no needed since the udp socket can receive datagrams without binding
    def bind(self, host, port):
        self.sock.bind((host, port))

    # This mehtod sends the message it gets as a parameter to ii.virtues.fi:23432
    # However, static receiver must be replaced with dynamic receiver i.e. in __init__ method
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
            cid, ack, eom, remaining, length, message = struct.unpack('!8s??HH64s', data[0])
            message = message[:length]
            return (message, eom)
        except Exception as e:
            print e
        

class TcpSocket:
    'Used for the first transmission via TCP'

    # Constructor - this method initializes the socket object
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    # This method sets up the connection - you need to call this in order to send or receive anything
    def connect(self, host, port):
        self.sock.connect((host, port))

    # This method sends blindly (no validation) message to the receiver
    def send(self, msg):
        self.sock.send(msg)

    # This method receives blindly (max 2048 bytes) message
    def receive(self):
        chunk = self.sock.recv(2048)
        return chunk            

    # This method closes the TCP connection
    # However, we should investigate whether this is enough for proper closing of TCP connection
    def close(self):
        self.sock.close()



############################### APPLICATION LOGIC
############################### Add methods used in main right below this
############################### so that they are introduced before actually used

# This method takes string as parameter, splits it into list of words by whitespaces
# and passes the list to parse_to_string(list) -method, which ties the list of words
# into one string and returns it
def reverse_message(message):
    size = len(message.split())
    duplicate = message.split()
    duplicate.reverse()
    # print duplicate
    return parse_to_string(duplicate)

def parse_to_string(list):
    newstr = ""
    for n in range(len(list)):
        newstr += list[n]
        if n < (len(list) - 1):
            newstr += " "
    return newstr

# For developement purposes address and port hardcoded
address = "ii.virtues.fi"
tcpPort = 10000

# Creating an instance of TCP Socket, connecting it to the server and sending a message
tsocket = TcpSocket()
tsocket.connect(address, tcpPort)
tsocket.send("HELLO\r\n")

# Catching and printing the response from TCP Socket
received = tsocket.receive()
print "Received: ", received

# Taking the necessary parameters out of the message (cid and UDP port)
msg, cid, udpPort = received.split()
print msg
print cid
print udpPort

# Now we can create an instance of UDP Socket
# Note that at this point we should input the UDP port to the socket - at the moment it is hardcoded
usocket = UdpSocket(cid)

try:
    hellomsg = "Hello from "
    hellomsg += cid
    usocket.send(hellomsg)
    while True:
        message, eof = usocket.receive()
        print "Eof: ", eof
        if eof:
            print "Last message: ", message
            break
        else:
            revmsg = reverse_message(message)
            print "New message to be sent: ", revmsg
            usocket.send(revmsg)

except Exception as e:
    print "Something is wrong with your class: ", e

finally:
    tsocket.close()
    print "Closing..."
    
