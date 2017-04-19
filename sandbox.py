# -*- coding: utf-8 -*-

import socket





ws = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
