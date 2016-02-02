#!/usr/bin/python
import socket
import os
import time
from GameRoomPacket.GRPacket import GRPacket
class GameRoom:
    def __init__(self, roomId, roomType):
        self.roomId = roomId
        self.roomType = roomType
        self.admin = ''
        self.userList = []
        self.msgQueueList = {}
    def SetAdmin(self, username):
        self.admin = username
    def AddUser(self, username):
        if username in self.userList:
            return False
        else:
            self.userList.append(username)
            self.msgQueueList[username] = []
            self.GenRoomInfoUpdate()
            return True
    def RemoveUser(self, username):
        try:
            self.userList.remove(username)
            del self.msgQueueList[username]
            return True
        except Exception as e:
            print 'Exception' + str(e) + 'raised when remove user' + username
            return False
    def GenRoomInfoUpdate(self):
        pkt = GRPacket()
        pkt.MakeUpdateRoomInfoRespond(self.roomId, self.admin, self.userList)
        for q in self.msgQueueList.itervalues():
            q.append(pkt)
    def GetOneMsg(self, username):
        if len(self.msgQueueList[username]) == 0:
            sdpkt = GRPacket('GR_EMPTY')
            return sdpkt
        else:
            return self.msgQueueList[username].pop(0)
    def ParsePacket(self, rcvpkt):
        assert rcvpkt.GetRoomId() == self.roomId
        if rcvpkt.IsAskOneMessage():
            username = rcvpkt.GetUser()
            self.AddUser(username)
            return self.GetOneMsg(username)
        elif rcvpkt.IsJoinRoom():
            username = rcvpkt.GetUser()
            self.AddUser(username)
            sdpkt = GRPacket('GR_SUCCESS')
            return sdpkt
        else:
            sdpkt = GRPacket('GR_FAIL')
            return sdpkt

class GameRoomList:
    def __init__(self):
        self.rooms = []
    def __contains__(self, roomid):
        return any([room.roomId == roomid for room in self.rooms])
    def __getitem__(self, k):
        if k >= len(self.rooms):
            raise IndexError
        else:
            return self.rooms[k]
    def AddRoom(self, username, roomid, roomType):
        if roomid in self.rooms:
            raise Exception("Added a room with same room number")
        else:
            newRoom = GameRoom(roomid, roomType)
            newRoom.SetAdmin(username)
            newRoom.AddUser(username)
            self.rooms.append(newRoom)
    def GetRoom(self, roomid):
        if roomid in self:
            for room in self.rooms:
                if room.roomId == roomid:
                    return room
            assert False
        else:
            return None
    def ParsePacket(self, rcvpkt):
        assert rcvpkt.IsToRoom()
        roomid = rcvpkt.GetRoomId()
        selectRoom = self.GetRoom(roomid)
        if selectRoom is not None:
            sdpkt = selectRoom.ParsePacket(rcvpkt)
            return sdpkt
        else:
            sdpkt = GRPacket('GR_FAIL')
            return sdpkt
        assert False


class GameRoomServer:
    def __init__(self):
        self.roomList = GameRoomList()
        self.currRoomId = 10000
        self.validRoomType = ['chat_room']
    def CreateRoom(self, username, roomType):
        self.roomList.AddRoom(username, str(self.currRoomId), roomType)
        if roomType in self.validRoomType: 
            self.roomList.AddRoom(username, str(self.currRoomId), roomType)
            print 'Created a new room %d by %s' % (self.currRoomId, username)
            self.currRoomId += 1
            return self.currRoomId - 1
        else:
            raise Exception("roomType %s wrong or roomid %d duplicate" % (roomType, self.currRoomId))
    def GetRoomList(self):
        roomlst = []
        for room in self.roomList:
            data = {}
            data['roomid'] = room.roomId
            data['roomType'] = room.roomType
            data['roomAdmin'] = room.admin
            roomlst.append(data)
        return roomlst
    def HasRoom(self, roomid):
        return roomid in self.roomList
    def ParseData(self, data):
        rcvpkt = GRPacket(data)
        sdpkt  = GRPacket('GR_FAIL')
        assert rcvpkt.IsRequest()
        if rcvpkt.IsToServer():
            if rcvpkt.IsInitTest():
                sdpkt.MakeInitTestRespond()
            elif rcvpkt.IsCreateRoom() :
                user = rcvpkt.GetUser()
                roomType = rcvpkt.GetRoomType()
                roomid = self.CreateRoom(user, roomType)
                sdpkt.MakeCreateRoomRespond(username = user, roomid = roomid)
            elif rcvpkt.IsCheckRoomId():
                roomid = rcvpkt.GetRoomId()
                hasRoomId = self.HasRoom(roomid)
                sdpkt.MakeHasRoomRespond(roomid, result = hasRoomId)
            elif rcvpkt.IsGetRoomList():
                roomList = self.GetRoomList()
                sdpkt.MakeGetRoomListRespond(roomList)
            else:
                sdpkt.MakeFailRespond()
        elif rcvpkt.IsToRoom:
            sdpkt = self.roomList.ParsePacket(rcvpkt)
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
        #try:
        resppkt = grServer.ParseData(data)
        #except Exception as e:
        #    print 'Got an exception!', e, 'when reading input data'
        #    print data
        #    resppkt = GRPacket('GR_FAIL')
        print "Send data :" + (resppkt.Serialize())
        connection.send(resppkt.Serialize())
