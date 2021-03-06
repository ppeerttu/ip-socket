# -*- coding: utf-8 -*-

import socket
import struct
import random

class UdpSocket:
    'Used for sending UDP datagrams'

    # Constructor - this method initializes the socket object
    def __init__(self, cid, keys_generated, keys_received, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = sock
        self.cid = cid
        self.keys_generated = keys_generated
        self.keys_received = keys_received


    # This mehtod sends the message it gets as a parameter to ii.virtues.fi:23432
    # However, static receiver must be replaced with dynamic receiver i.e. in __init__ method
    def send(self, message, ack):
        
        # Calculate the length of the actual message in bytes
        length = len(message)
        print "Length of the whole message: ", length
        
        while True:
            partialmsg = ""
            partiallen = 0
            ack = ack
            eom = False
            if length > 64:
                partialmsg = message[:64]
                message = message[64:]
                partiallen = len(partialmsg)
                length -= 64
            else:
                partialmsg = message
                partiallen = len(partialmsg)
                length -= partiallen
            print "Length of remaining message: ", length
            
            # Add null characters until the full length of the message is 64 bytes
            for n in range(64 - partiallen):
                partialmsg += '\0'

            partialmsg = self.encrypt(partialmsg, self.keys_generated[0])
            self.keys_generated.remove(self.keys_generated[0])
            print "Self-generated keys remaining: ", len(self.keys_generated)
            remaining = length

            #partialmsg = self.parity_message(partialmsg)
            #checkpar, x = self.check_parity(partialmsg)
            #print "Parity completed successfully: ", checkpar
            # Pack the data into raw format and send it to the receiver
            # Headers size 8 + 1 + 1 + 2 + 2 = 14 bytes
            data = struct.pack('!8s??HH64s', cid, ack, eom, remaining, partiallen, partialmsg)
            self.sock.sendto(data, ("ii.virtues.fi", 23432))
            print "Remaining: ", remaining
            if remaining == 0:
                break

    def encrypt(self, message, key):
        crypted = ""
        for n in range(len(message)):
            crypted += chr(ord(message[n]) ^ ord(key[n]))
        return crypted

    def receive(self):
        message = ""
        while True:
            # Listen to socket max 78 bytes - 64 + 14 (headers)
            data = self.sock.recvfrom(78)
            print "Data: ", data
            # Unpack the raw data into understantable form
            # Header size 14 bytes
            cid, ack, eom, remaining, length, partialmessage = struct.unpack('!8s??HH64s', data[0])
            partialmessage = partialmessage[:length]
            print "Received length: ", length
            print "Received remaining: ", remaining

            # The last message from the server (EOM) has no parity nor encryption
            if eom:
                return (partialmessage, eom)
            
            #correctparity, partialmessage = self.check_parity(partialmessage)
            correctparity = True
            if not correctparity:
                print "Parity incorrect!"
                self.send("Send again", False)
                self.keys_received.remove(self.keys_received[0])
            else:
                partialmessage = self.decrypt(partialmessage, self.keys_received[0])
                self.keys_received.remove(self.keys_received[0])
                message = message + partialmessage
                if remaining == 0:
                    print "The whole, decrypted message: ", message
                    return (message, eom)

    def decrypt(self, message, key):
        decrypted = ""
        for n in range (len(message)):
            decrypted += chr(ord(message[n]) ^ ord(key[n]))
        return decrypted

    def get_parity(self, char):
        while char > 1:
            char = (char >> 1) ^ (char & 1)
        return char

    def check_parity(self, message):
        unparity = ""
        for n in range(len(message)):
            x = ord(message[n])
            paritybit = x & 1
            x >>= 1
            unparity += chr(x)
            if not paritybit == self.get_parity(x):
                return (False, unparity)
        return (True, unparity)


    def parity_message(self, message):
        paritymessage = ""
        for n in message:
            x = ord(n)
            #print "Before: ", bin(x)
            x <<= 1
            x += self.get_parity(x)
            #print "After: ", bin(x)
            paritymessage += chr(x)

        return paritymessage

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

    

# Generating one encryption key of 64 bytes
def generate_encrypt_key():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    key = ""
    for n in range(64):
        key += characters[random.randint(0, len(characters) - 1)]
    return key




# For developement purposes address and port hardcoded
address = "ii.virtues.fi"
tcpPort = 10000
keys_generated = []

# Creating an instance of TCP Socket, connecting it to the server and sending a message
tsocket = TcpSocket()
tsocket.connect(address, tcpPort)
tsocket.send("HELLO ENC MUL\r\n")

for n in range(20):
        key = generate_encrypt_key()
        keys_generated.append(key)
        key += "\r\n"
        tsocket.send(key)
tsocket.send(".\r\n")

# Catching and printing the response from TCP Socket (includes cid, port, and encryption keys)
received = tsocket.receive()


# Taking the necessary parameters and keys out of the message
keys_received = []
keys_received = received.split()

cid = keys_received[1]
port = keys_received[2]
message = keys_received[0]

# Remove cid, port etc to leave only the encryption keys to the list
keys_received.remove(message)
keys_received.remove(port)
keys_received.remove(cid)
keys_received.remove(".")

print keys_received
print "Length: ", len(keys_received)




# Now we can create an instance of UDP Socket
# Note that at this point we should input the UDP port to the socket - at the moment it is hardcoded
usocket = UdpSocket(cid, keys_generated, keys_received)

#test = "Message1"
#test = usocket.parity_message(test)
#print "Paritymessage: ", test
#for n in test:
#    print bin(ord(n))
#check = usocket.check_parity(test)
#print "Parity: ", check
#print bin(usocket.get_parity(3))
#print bin(3)


try:
    # Sending the first message
    print "Try -block"
    hellomsg = "Hello from "
    hellomsg += cid
    usocket.send(hellomsg, True)
    
    # Loop: 1. Receiving (encrypted) message
    # 2. Checking whether or not the message will be the last one - if yes, no need for decryption, just print the message and break
    # 3. Decrypting the message and deleting the used decryption key
    # 4. Reversing the message and encrypting it back
    # 5. Sending the message back and removing the encryption key
    while True:
        message, eom = usocket.receive()
        if eom:
            print "Last message: ", message
            break

        revmsg = reverse_message(message)
        print "New message to be sent: ", revmsg
        usocket.send(revmsg, True)

except Exception as e:
    print "Something is wrong with your class: ", e

finally:
    tsocket.close()
    print "Closing..."
    
