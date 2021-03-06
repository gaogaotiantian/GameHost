import json
'''
status = 'Success' or 'Fail'
    whether intended behavior worked correctly
direction = 'Request' or 'Respond'
    From web to GameRoom = 'Request' and From GameRoom to web = 'Respond'
type = 
    --'InitTest'
        -- 'data' = 'Test'
            Initialization packet from server to gameroom
        -- 'data' = 'Ready'
            Ready signal from gameroom
    --'CreateRoom'
        -- 'user' is the user to create the room
    --'CheckRoomId'
        -- 'result' is whether roomid exists
'''
class GRPacket:
    def __init__(self, data = ''):
        self.data = {}
        self.validGeneralType = ['AskOneMessage', 'Empty']
        self.validServerType = ['InitTest', 'CreateRoom', 'CheckRoomId', 'UpdateRoomInfo', 'GetRoomList', 'JoinRoom']
        self.validGameroomType = ['PostChat', 'LeaveRoom', 'KickUserList', 'InvalidRoom', 'GameInfo', 'StartGame', 'GameExist', 'GetGameInfo']
        self.validGomokuType = ['GomokuMove', 'GomokuRestart']
        self.validRoomType = ['chat_room', 'gomoku_room']
        self.validTarget = ['server', 'room_generic', 'room_gomoku', 'host', 'front_end']
        if data == '':
            self.data['status'] = 'Success'
        elif data.startswith('GR_'):
            if data == 'GR_FAIL':
                self.MakeFailRespond()
            elif data == 'GR_SUCCESS':
                self.MakeSuccessRespond()
            elif data == 'GR_EMPTY':
                self.MakeEmptyRespond()
            elif data == 'GR_INVALIDROOM':
                self.MakeInvalidRoomRespond()
            else:
                raise Exception('Unknown Initialization!', data)
        else:
            self.Deserialize(data)
    def SetSuccess(self):
        self.data['status'] = 'Success'
    def SetFail(self):
        self.data['status'] = 'Fail'
    def SetRequest(self):
        self.data['direction'] = 'Request'
    def SetRespond(self):
        self.data['direction'] = 'Respond'
    def SetType(self, t):
        if (t in self.validGeneralType or 
            t in self.validGameroomType or
            t in self.validGomokuType or 
            t in self.validServerType):
            self.data['type'] = t
        else:
            raise Exception('Wrong type!', t)
    def GetType(self):
        if self.data['type'] != '':
            return self.data['type'] 
        else:
            raise Exception('No type!')
    def SetTarget(self, target):
        if target in self.validTarget:
            self.data['target'] = target
        else:
            raise Exception('Wrong target!', target)
    def GetTarget(self):
        return self.data['target']
    def SetRoomType(self, roomType):
        if roomType in self.validRoomType:
            self.data['roomType'] = roomType
        else:
            raise Exception("Not valid room type!")
    def GetRoomType(self):
        return self.data['roomType']

    def SetData(self, dataKey, dataValue):
        self.data[dataKey] = dataValue
    def GetData(self, dataKey):
        if dataKey in self.data:
            return self.data[dataKey]
        else:
            raise Exception("No data key for " + dataKey)
    def SetUser(self, username):
        self.data['username'] = username
    def GetUser(self):
        return self.data['username']
    def SetRoomAdmin(self, roomAdmin):
        self.data['roomAdmin'] = roomAdmin
    def GetRoomAdmin(self):
        return self.data['roomAdmin']
    def SetRoomId(self, roomid):
        self.data['roomid'] = roomid
    def GetRoomId(self):
        return self.data['roomid']
    def SetRoomList(self, roomList):
        self.data['roomList'] = roomList
    def GetRoomList(self):
        return self.data['roomList']
    def SetResult(self, result):
        self.data['result'] = result
    def GetResult(self):
        if (self.data['type'] == 'CheckRoomId' or 
                self.data['type'] == 'GameExist'):
            return self.data['result']
        else:
            raise Exception("Tried to read result when not supposed to")
    def SetUserList(self, userList):
        self.data['userList'] = userList
    def GetUserList(self):
        return self.data['userList']
    def SetGameInfo(self, gameInfo):
        self.data['gameInfo'] = gameInfo
    def GetGameInfo(self, gameInfo):
        return self.data['gameInfo']
    def SetMsg(self, msg):
        self.data['msg'] = msg
    def GetMsg(self):
        return self.data['msg']
    # Is functions with Get*()
    def IsType(self, t):
        if (t in self.validGeneralType or 
            t in self.validGameroomType or
            t in self.validGomokuType or 
            t in self.validServerType):
            return self.data['type'] == t
        else:
            raise Exception("Wrong type", t)

    def IsInitTest(self):
        return self.GetType() == 'InitTest'
    def IsSuccess(self):
        return self.data['status'] == 'Success'
    def IsFail(self):
        return self.data['status'] == 'Fail'
    def IsRequest(self):
        return self.data['direction'] == 'Request'
    def IsRespond(self):
        return self.data['direction'] == 'Respond'
    def IsEmpty(self):
        return self.GetType() == 'Empty'
    # Target Check
    def IsToServer(self):
        return self.GetTarget() == 'server'
    def IsToRoom(self):
        return self.GetTarget().startswith('room')
    def IsToGomoku(self):
        return self.GetTarget() == 'room_gomoku'
    # Directly make a packet using internal functions
    def MakeInitTestRequest(self):
        self.SetSuccess()
        self.SetRequest()
        self.SetTarget('server')
        self.SetType('InitTest')
    def MakeInitTestRespond(self):
        self.SetSuccess()
        self.SetRespond()
        self.SetTarget('host')
        self.SetType('InitTest')
    def MakeCreateRoomRequest(self, username, roomType):
        self.SetRequest()
        self.SetType('CreateRoom')
        self.SetTarget('server')
        self.SetRoomType(roomType)
        self.SetUser(username)
    def MakeCreateRoomRespond(self, username, roomid):
        self.SetSuccess()
        self.SetRespond()
        self.SetTarget('host')
        self.SetType('CreateRoom')
        self.SetUser(username)
        self.SetRoomId(roomid)
    def MakeHasRoomRequest(self, roomid):
        self.SetRequest()
        self.SetTarget('server')
        self.SetType('CheckRoomId')
        self.SetRoomId(roomid)
    def MakeHasRoomRespond(self, roomid, result):
        self.SetSuccess()
        self.SetRespond()
        self.SetTarget('host')
        self.SetType('CheckRoomId')
        self.SetRoomId(roomid)
        self.SetResult(result)
    def MakeGetRoomInfoRequest(self, roomid):
        self.SetRequest()
        self.SetTarget('server')
        self.SetType('GetRoomInfo')
        self.SetRoomId(roomid)
    def MakeGetRoomInfoRespond(self, roomid, roomAdmin, userList):
        self.SetSuccess()
        self.SetRespond()
        self.SetTarget('host')
        self.SetType('GetRoomInfo')
        self.SetRoomId(roomid)
        self.SetRoomAdmin(roomAdmin)
        self.SetUserList(userList)
    def MakeAskOneMessageRequest(self, roomid, username, target):
        self.SetRequest()
        self.SetTarget(target)
        self.SetType('AskOneMessage')
        self.SetRoomId(roomid)
        self.SetUser(username)
    def MakeUpdateRoomInfoRespond(self, roomid, roomAdmin, userList):
        self.SetSuccess()
        self.SetRespond()
        self.SetTarget('front_end')
        self.SetType('UpdateRoomInfo')
        self.SetRoomId(roomid)
        self.SetRoomAdmin(roomAdmin)
        self.SetUserList(userList)
    def MakeGetRoomListRequest(self):
        self.SetRequest()
        self.SetTarget('server')
        self.SetType('GetRoomList')
    def MakeGetRoomListRespond(self, roomList):
        self.SetSuccess()
        self.SetRespond()
        self.SetTarget('front_end')
        self.SetType('GetRoomList')
        self.SetRoomList(roomList)
    def MakeJoinRoomRequest(self, username, roomid):
        self.SetRequest()
        self.SetTarget('room_generic')
        self.SetType('JoinRoom')
        self.SetRoomId(roomid)
        self.SetUser(username)
    def MakePostChatRequest(self, roomid, username, msg):
        self.SetRequest()
        self.SetTarget('room_generic')
        self.SetType('PostChat')
        self.SetRoomId(roomid)
        self.SetUser(username)
        self.SetMsg(msg)
    def MakePostChatRespond(self, roomid, username, msg):
        self.SetRespond()
        self.SetTarget('front_end')
        self.SetType('PostChat')
        self.SetRoomId(roomid)
        self.SetUser(username)
        self.SetMsg(msg)
    def MakeLeaveRoomRequest(self, roomid, username):
        self.SetRequest()
        self.SetTarget('room_generic')
        self.SetType('LeaveRoom')
        self.SetRoomId(roomid)
        self.SetUser(username)
    def MakeKickUserListRequest(self, roomid, userList):
        self.SetRequest()
        self.SetTarget('room_generic')
        self.SetType('KickUserList')
        self.SetRoomId(roomid)
        self.SetUserList(userList)
    def MakeStartGameRequest(self, roomid, userList):
        self.SetRequest()
        self.SetTarget('room_generic')
        self.SetType('StartGame')
        self.SetRoomId(roomid)
        self.SetUserList(userList)
    def MakeGameExistRequest(self, roomid):
        self.SetRequest()
        self.SetTarget('room_generic')
        self.SetType('GameExist')
        self.SetRoomId(roomid)
    def MakeGetGameInfoRequest(self, roomid, target):
        self.SetRequest()
        self.SetTarget(target)
        self.SetRoomId(roomid)
        self.SetType('GetGameInfo')
    def MakeGameExistRespond(self, result):
        self.SetSuccess()
        self.SetRespond()
        self.SetTarget('server')
        self.SetType('GameExist')
        self.SetResult(result)
    # Gomoku related
    def MakeGomokuMoveRequest(self, roomid, username, x, y):
        self.SetRequest()
        self.SetTarget('room_gomoku')
        self.SetType('GomokuMove')
        self.SetRoomId(roomid)
        self.SetData('username', username)
        self.SetData('x', x)
        self.SetData('y', y)
    def MakeGomokuInfoRespond(self, gameInfo):
        self.SetRespond()
        self.SetSuccess()
        self.SetTarget('front_end')
        self.SetType('GameInfo')
        self.SetGameInfo(gameInfo)
    # Gomoku end
    def MakeEmptyRespond(self):
        self.SetSuccess()
        self.SetTarget('front_end')
        self.SetType('Empty')
    def MakeSuccessRespond(self):
        self.SetSuccess()
        self.SetRespond()
    def MakeFailRespond(self):
        self.SetFail()
        self.SetRespond()
    def MakeInvalidRoomRespond(self):
        self.SetFail()
        self.SetRespond()
        self.SetType('InvalidRoom')
    def Serialize(self):
        return json.dumps(self.data)
    def Deserialize(self, data):
        self.data = json.loads(data)
