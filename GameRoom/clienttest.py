import socket
import time

if __name__ == "__main__":
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn = '/tmp/GameRoomConn'
    sock.connect(conn)
    time.sleep(1)
    sock.send('hello world')
    sock.close()
