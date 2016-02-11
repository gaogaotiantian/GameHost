#!/usr/bin/python
import socket
import os
import time
from GameRoomPacket.GRPacket import GRPacket
from User import User
from Gomoku import Gomoku

class GameRoom:
    def __init__(self, roomid, roomType):
        self.roomid = roomid
        self.roomType = roomType
        self.game = None
        self.admin = ''
        self.userList = {}
        self.msgQueueList = {}
        self.userClearTime = 5
        self.checkInterval = 10
        self.lastCheckTime = time.time()
    def SetAdmin(self, username):
        self.admin = username
    def GetAdmin(self):
        return self.admin
    def HasAdmin(self):
        return self.HasUser(self.GetAdmin())
    def AddUser(self, username):
        if username in self.userList:
            self.GenRoomInfoUpdate()
            return False
        else:
            self.userList[username] = User(username)
            self.GenRoomInfoUpdate()
            return True
    def HasUser(self, username):
        return username in self.userList
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
    def SendPktToEveryone(self, pkt):
        for user in self.userList.itervalues():
            user.AddMsg(pkt)
    def GenRoomInfoUpdate(self):
        pkt = GRPacket()
        pkt.MakeUpdateRoomInfoRespond(self.roomid, self.admin, self.userList.keys())
        self.SendPktToEveryone(pkt)
    def GetOneMsg(self, username):
        self.CheckEverything()
        if username in self.userList:
            return self.userList[username].GetMsg()
        else:
            return GRPacket('GR_INVALIDROOM')
    def GetUserNum(self):
        return len(self.userList)
    def StartGame(self, playerList):
        if self.roomType == 'gomoku_room':
            if len(playerList) == 2:
                self.game = Gomoku(playerList, self.userList)
                self.game.StartGame(playerList)
                return GRPacket('GR_SUCCESS')
        return GRPacket('GR_FAIL')
    def PostChat(self, username, msg):
        pkt = GRPacket()
        pkt.MakePostChatRespond(self.roomid, username, msg)
        self.SendPktToEveryone(pkt)
    def ParsePacket(self, rcvpkt):
        assert rcvpkt.GetRoomId() == self.roomid
        if rcvpkt.IsToGomoku():
            if self.game != None:
                return self.game.ParsePacket(rcvpkt)
            else:
                return GRPacket('GR_FAIL')
        elif rcvpkt.IsType('AskOneMessage'):
            username = rcvpkt.GetUser()
            return self.GetOneMsg(username)
        elif rcvpkt.IsType('JoinRoom'):
            username = rcvpkt.GetUser()
            self.AddUser(username)
            return GRPacket('GR_SUCCESS')
        elif rcvpkt.IsType('PostChat'):
            username = rcvpkt.GetUser()
            msg = rcvpkt.GetMsg()
            self.PostChat(username, msg)
            return GRPacket('GR_SUCCESS')
        elif rcvpkt.IsType('LeaveRoom'):
            username = rcvpkt.GetUser()
            self.RemoveUserList([username])
            return GRPacket('GR_SUCCESS')
        elif rcvpkt.IsType('GameExist'):
            sdpkt = GRPacket()
            if self.game == None:
                sdpkt.MakeGameExistRespond(False)
            else:
                sdpkt.MakeGameExistRespond(True)
            return sdpkt
        elif rcvpkt.IsType('KickUserList'):
            userList = rcvpkt.GetUserList()
            self.RemoveUserList(userList)
            return GRPacket('GR_SUCCESS')
        elif rcvpkt.IsType('StartGame'):
            playerList = rcvpkt.GetUserList()
            self.StartGame(playerList)
            return self.StartGame(playerList)
        else:
            sdpkt = GRPacket('GR_FAIL')
            return sdpkt

class GameRoomServer:
    def __init__(self):
        self.roomList = {}
        self.currRoomId = 10000
        self.validRoomType = ['chat_room', 'gomoku_room']
        self.lastCheckTime = time.time()
        self.checkInterval = 10
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
            print type(roomType)
            print self.validRoomType, roomType

            raise Exception("roomType %s wrong or roomid %d duplicate" % (roomType, self.currRoomId))
    def RemoveRoom(self, roomid):
        if roomid in self.roomList:
            del self.roomList[roomid]
        else:
            raise Exception("Try to remove room %s but it did not exist" % roomid)
    def GetRoomList(self):
        roomlst = {}
        for room in self.roomList.itervalues():
            data = {}
            data['roomid'] = room.roomid
            data['roomType'] = room.roomType
            data['roomAdmin'] = room.admin
            roomlst[room.roomid] = data
        return roomlst
    def HasRoom(self, roomid):
        return roomid in self.roomList
    def CheckEmptyRoom(self):
        rmvIdList = []
        for roomid in self.roomList:
            self.roomList[roomid].CheckEverything()
            if (self.roomList[roomid].GetUserNum() == 0 or
                    not self.roomList[roomid].HasAdmin()):
                rmvIdList.append(roomid)
        for rmvId in rmvIdList:
            self.RemoveRoom(rmvId)
    def CheckEverything(self):
        if time.time() - self.lastCheckTime > self.checkInterval:
            self.lastCheckTime = time.time()
            self.CheckEmptyRoom()
    def ParseData(self, data):
        rcvpkt = GRPacket(data)
        sdpkt  = GRPacket('GR_FAIL')
        self.CheckEverything()
        assert rcvpkt.IsRequest()
        # If the packet is for server
        if rcvpkt.IsToServer():
            if rcvpkt.IsType('InitTest'):
                sdpkt.MakeInitTestRespond()
            elif rcvpkt.IsType('CreateRoom') :
                user = rcvpkt.GetUser()
                roomType = rcvpkt.GetRoomType()
                roomid = self.CreateRoom(user, roomType)
                sdpkt.MakeCreateRoomRespond(username = user, roomid = roomid)
            elif rcvpkt.IsType('CheckRoomId'):
                roomid = rcvpkt.GetRoomId()
                hasRoomId = self.HasRoom(roomid)
                sdpkt.MakeHasRoomRespond(roomid, result = hasRoomId)
            elif rcvpkt.IsType('GetRoomList'):
                roomList = self.GetRoomList()
                sdpkt.MakeGetRoomListRespond(roomList)
            else:
                sdpkt.MakeFailRespond()
        # If the packet is for a specific room
        elif rcvpkt.IsToRoom():
            roomid = rcvpkt.GetRoomId()
            if self.HasRoom(roomid):
                sdpkt = self.roomList[roomid].ParsePacket(rcvpkt)
            else:
                sdpkt = GRPacket('GR_INVALIDROOM')
        return sdpkt


if __name__ == "__main__":
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn = '/home/gaotian/Programs/GameHost/GameRoomConn'
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
        try:
            print "Send data :" + (resppkt.Serialize())
        except Exception as e:
            print e, resppkt
        connection.send(resppkt.Serialize())
