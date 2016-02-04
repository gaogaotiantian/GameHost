#!/usr/bin/python
import socket
import os
import time
from GameRoomPacket.GRPacket import GRPacket
class User:
    def __init__(self, username):
        self.lastActivate = time.time()
        self.username = username
        self.msgList = []
    def AddMsg(self, pkt):
        self.msgList.append(pkt)
    def GetMsg(self):
        self.Refresh()
        if len(self.msgList) == 0:
            return GRPacket('GR_EMPTY')
        else:
            return self.msgList.pop(0)
    def Refresh(self):
        self.lastActivate = time.time()
    def CheckTimeInterval(self, interval):
        return time.time() - self.lastActivate > interval

class GameRoom:
    def __init__(self, roomid, roomType):
        self.roomid = roomid
        self.roomType = roomType
        self.admin = ''
        self.userList = {}
        self.msgQueueList = {}
        self.userClearTime = 5
        self.checkInterval = 10
        self.lastCheckTime = time.time()
    def SetAdmin(self, username):
        self.admin = username
    def AddUser(self, username):
        if username in self.userList:
            self.GenRoomInfoUpdate()
            return False
        else:
            self.userList[username] = User(username)
            self.GenRoomInfoUpdate()
            return True
    def RemoveUser(self, username):
        try:
            del self.userList[username]
            return True
        except Exception as e:
            print 'Exception' + str(e) + 'raised when remove user' + username
            return False
    def RemoveUserList(self, usernameList):
        if usernameList == []:
            return True
        try:
            for username in usernameList:
                self.RemoveUser(username)
            self.GenRoomInfoUpdate()
            return True
        except Exception as e:
            print 'Exception' + str(e) + 'raised when remove usernameList' + usernameList
            return False
    def CheckAllUsers(self):
        rUserList = []
        for user in self.userList:
            if self.userList[user].CheckTimeInterval(self.userClearTime):
                rUserList.append(user)
        self.RemoveUserList(rUserList)
    def CheckEverything(self):
        if time.time() - self.lastCheckTime > self.checkInterval:
            self.lastCheckTime = time.time()
            self.CheckAllUsers();
    def GenRoomInfoUpdate(self):
        pkt = GRPacket()
        pkt.MakeUpdateRoomInfoRespond(self.roomid, self.admin, self.userList.keys())
        for user in self.userList.itervalues():
            user.AddMsg(pkt)
    def GetOneMsg(self, username):
        self.CheckEverything()
        if username in self.userList:
            return self.userList[username].GetMsg()
        else:
            return GRPacket('GR_FAIL')
    def ParsePacket(self, rcvpkt):
        assert rcvpkt.GetRoomId() == self.roomid
        if rcvpkt.IsAskOneMessage():
            username = rcvpkt.GetUser()
            return self.GetOneMsg(username)
        elif rcvpkt.IsJoinRoom():
            username = rcvpkt.GetUser()
            self.AddUser(username)
            sdpkt = GRPacket('GR_SUCCESS')
            return sdpkt
        else:
            sdpkt = GRPacket('GR_FAIL')
            return sdpkt

class GameRoomServer:
    def __init__(self):
        self.roomList = {}
        self.currRoomId = 10000
        self.validRoomType = ['chat_room']
    def CreateRoom(self, username, roomType):
        if roomType in self.validRoomType: 
            roomid = str(self.currRoomId)
            newRoom = GameRoom(roomid, roomType)
            newRoom.SetAdmin(username)
            newRoom.AddUser(username)
            self.roomList[roomid] = newRoom
            print 'Created a new room %d by %s' % (self.currRoomId, username)
            self.currRoomId += 1
            return roomid
        else:
            raise Exception("roomType %s wrong or roomid %d duplicate" % (roomType, self.currRoomId))
    def GetRoomList(self):
        roomlst = []
        for room in self.roomList.itervalues():
            data = {}
            data['roomid'] = room.roomid
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
        # If the packet is for server
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
        # If the packet is for a specific room
        elif rcvpkt.IsToRoom:
            roomid = rcvpkt.GetRoomId()
            if self.HasRoom(roomid):
                sdpkt = self.roomList[roomid].ParsePacket(rcvpkt)
            else:
                sdpkt = GRPacket('GR_FAIL')
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
