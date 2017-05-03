# -*- coding: utf-8 -*-

import socket
import struct
import random
import sys


#######################
####################### Presenting the classes
#######################

class UdpSocket:
    'Used for sending UDP datagrams'

    # Constructor - this method initializes the socket object
    # Socket gets both self generated encrypt keys and received encrypt keys
    def __init__(self, ip, port, cid, keys_generated, keys_received, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = sock
        self.cid = cid
        self.keys_generated = keys_generated
        self.keys_received = keys_received
        self.port = port
        self.ip = ip

    # This method sends the message it gets as a parameter - gets the value of acknowledgement as a parameter also
    def send(self, message, ack):
        print "Sending!\n"
        
        # Calculate the length of the actual message in bytes
        length = len(message)
        
        # Enter into sending loop - necessary for multipart messages
        while True:
            partialmsg = ""
            partiallen = 0
            eom = False
            # Dealing with the message length (if over 64 bytes we gotta slice it up)
            if length > 64:
                partialmsg = message[:64]
                message = message[64:]
                partiallen = len(partialmsg)
                length -= 64
            else:
                partialmsg = message
                partiallen = len(partialmsg)
                length -= partiallen
            
            # Add null characters until the full length of the message is 64 bytes
            for n in range(64 - partiallen):
                partialmsg += '\0'

            # Ecnrypt the message and remove the used key from self-generated key list
            partialmsg = self.encrypt(partialmsg, self.keys_generated[0])
            self.keys_generated.remove(self.keys_generated[0])

            remaining = length
            
            # Parity the encrypted message
            partialmsg = self.parity_message(partialmsg)

            # Pack the data into raw format and send it to the receiver
            # Headers size 8 + 1 + 1 + 2 + 2 = 14 bytes
            data = struct.pack('!8s??HH64s', cid, ack, eom, remaining, partiallen, partialmsg)
            self.sock.sendto(data, (self.ip, self.port))
            if remaining == 0:
                break

    # Encrypt the message given as a parameter with a key given as a parameter
    def encrypt(self, message, key):
        crypted = ""
        for n in range(len(message)):
            crypted += chr(ord(message[n]) ^ ord(key[n]))
        return crypted

    # Handle incoming messages:
    # In the while -loop receive datagrams size of 78 bytes and unpack each individually
    # Message will be constructed from multiple datagrams if there is more than one incoming
    def receive(self):
        message = ""
        print "Data incoming!"
        while True:
            # Listen to socket max 78 bytes - 64 + 14 (headers)
            data = self.sock.recvfrom(78)
            # Unpack the raw data into understandable form
            # Header size 14 bytes
            cid, ack, eom, remaining, length, partialmessage = struct.unpack('!8s??HH64s', data[0])
            partialmessage = partialmessage[:length]

            message = message + partialmessage
            if remaining == 0:
                break

        # The last message from the server (EOM) has no parity nor encryption
        if eom:
            return (message, eom, True)
        
        # Check the parity and decrypt the message
        correctparity, message = self.check_parity(message)
        message = self.decrypt(message)

        # If parity incorrect
        if not correctparity:
            print "Parity incorrect!"
            return ("Send again", eom, False)
        
        # Otherwise
        else:
            return (message, eom, True)

    # Decrypt the message given as a parameter
    # Note: This method takes care of the encryption keys
    def decrypt(self, rec_message):
        key = self.keys_received[0]
        self.keys_received.remove(self.keys_received[0])
        if len(rec_message) > 64:
            key = key + self.keys_received[0]
            self.keys_received.remove(self.keys_received[0])
        if len(rec_message) > 128:
            key = key + self.keys_received[0]
            self.keys_received.remove(self.keys_received[0])
        decrypted = ""
        for n in range (len(rec_message)):
            decrypted += chr(ord(rec_message[n]) ^ ord(key[n]))
        return decrypted

    # Raw tool method: return a bit of value 1 if the character given as a parameter
    # has uneven number of 1 bits
    def get_parity(self, char):
        while char > 1:
            char = (char >> 1) ^ (char & 1)
        return char

    # Check the parity of the message given as a parameter and return True or False
    # regarding the parity was correct or incorrect
    def check_parity(self, message):
        unparity = ""
        pass_parity = True
        for n in range(len(message)):
            x = ord(message[n])
            paritybit = x & 1
            x >>= 1
            unparity += chr(x)
            if not paritybit == self.get_parity(x):
                pass_parity = False
        return (pass_parity, unparity)

    # Parity the message
    def parity_message(self, message):
        paritymessage = ""
        for n in message:
            x = ord(n)
            x <<= 1
            x += self.get_parity(x)
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



############################### HELPER METHODS
###############################
###############################

# This method takes string as parameter, splits it into list of words by whitespaces
# and passes the list to parse_to_string(list) -method, which ties the list of words
# into one string and returns it
def reverse_message(message):
    size = len(message.split())
    duplicate = message.split()
    duplicate.reverse()
    # print duplicate
    return parse_to_string(duplicate)

# Helper method - ties a list of words into one string and returns it
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

#############################
############################# APPLICATION LOGIC
#############################

# Print a tip for the user
print "Information you're probably looking for: ii.virtues.fi:10000"

# Ask for address
# If the port number is not valid integer shut down the program
address = raw_input("Give an ip-address or domain name of the host: ")
try:
    tcpPort = int(raw_input("Port number: "))
except Exception as e:
    print "Input invalid! Port number should be an integer. Shutting down..."
    sys.exit()
keys_generated = []

# Creating an instance of TCP Socket, connecting it to the server and sending a message
# If user has set invalid host address shut down the program
tsocket = TcpSocket()
try:
    tsocket.connect(address, tcpPort)
except Exception as e:
    print "No host was found with your address. Shutting down..."
    sys.exit()

tsocket.send("HELLO ENC MUL PAR\r\n")

# Generating encryption keys and sending them
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
port = int(keys_received[2])
message = keys_received[0]

# Remove cid, port etc. to leave only the encryption keys to the list
keys_received.remove(message)
keys_received.remove(str(port))
keys_received.remove(cid)
keys_received.remove(".")

# Now we can create an instance of UDP Socket - the socket object holds the encryption keys
usocket = UdpSocket(address, port, cid, keys_generated, keys_received)

# Sending the first message
hellomsg = "Hello from "
hellomsg += cid
usocket.send(hellomsg, True)
    
# Loop: 1. Receiving (encrypted) message
# 2. Checking whether or not the message will be the last one - if yes, just print the message and break
# 3. Checking if parity check has failed - if yes, send the message back with False parity and go to step 1
# 4. Reversing the message
# 5. Printing the reversed message and sending it back
while True:
    message, eom, parity = usocket.receive()
    if eom:
        print "Last message: ", message
        break
    elif parity == False:
        usocket.send(message, False)
    else:
        print "The whole, decrypted message: ", message
        revmsg = reverse_message(message)
        print "New message to be sent: ", revmsg
        usocket.send(revmsg, True)

# Close the tcp socket and exit
tsocket.close()
print "Closing..."
    
