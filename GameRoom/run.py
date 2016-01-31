#!/usr/bin/python
import socket
import os
def ParseData(data):
    if data == 'Initial connection test':
        return 'Ready'
    else:
        return 'Unknown command'
if __name__ == "__main__":
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn = '/tmp/GameRoomConn'
    if not os.path.exists(conn):
        os.mknod(conn)
    if os.path.exists(conn):
        os.unlink(conn)
    sock.bind(conn)
    sock.listen(5)
    while True:
        connection, address = sock.accept()
        data = connection.recv(1024)
        print "Received data : " + data
        connection.send(ParseData(data))
