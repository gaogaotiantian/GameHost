#!/usr/bin/python
import socket
import os
import time
from GameRoomPacket.GRPacket import GRPacket
class GameRoom:
    def __init__(self, roomId):
        self.roomId = roomId
        self.admin = ''
    def SetAdmin(self, username):
        self.admin = username

class GameRoomList:
    def __init__(self):
        self.rooms = []
    def __contains__(self, roomid):
        return any([room.roomId == roomid for room in self.rooms])
    def AddRoom(self, username, roomid):
        if roomid in self.rooms:
            raise Exception("Added a room with same room number")
        else:
            newRoom = GameRoom(roomid)
            newRoom.SetAdmin(username)
            self.rooms.append(newRoom)
class GameRoomServer:
    def __init__(self):
        self.roomList = GameRoomList()
        self.currRoomId = 10000
    def CreateRoom(self, username):
        self.roomList.AddRoom(username, str(self.currRoomId))
        print 'Created a new room %d by %s' % (self.currRoomId, username)
        self.currRoomId += 1
        return self.currRoomId - 1
    def HasRoom(self, roomid):
        return roomid in self.roomList
    def ParseData(self, data):
        rcvpkt = GRPacket(data)
        sdpkt  = GRPacket()
        assert rcvpkt.IsRequest()
        if rcvpkt.IsInitTest():
            sdpkt.MakeInitTestResponse()
            return sdpkt
        elif rcvpkt.IsCreateRoom() :
            user = rcvpkt.GetUser()
            roomid = self.CreateRoom(user)
            sdpkt.MakeCreateRoomResponse(username = user, roomid = roomid)
            return sdpkt
        elif rcvpkt.IsCheckRoomId():
            roomid = rcvpkt.GetRoomId()
            hasRoomId = self.HasRoom(roomid)
            sdpkt.MakeHasRoomResponse(roomid, result = hasRoomId)
            return sdpkt
        else:
            sdpkt.MakeFailResponse()
            return sdpkt


if __name__ == "__main__":
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn = '/tmp/GameRoomConn'
    if not os.path.exists(conn):
        os.mknod(conn)
    if os.path.exists(conn):
        os.unlink(conn)
    sock.bind(conn)
    sock.listen(5)
    grServer = GameRoomServer()
    while True:
        connection, address = sock.accept()
        data = connection.recv(1024)
        print "Received data : " + data
        resppkt = grServer.ParseData(data)
        print "Send data :" + (resppkt.Serialize())
        connection.send(resppkt.Serialize())
