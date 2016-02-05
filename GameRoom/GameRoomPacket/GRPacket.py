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
        self.validType = ['InitTest', 'CreateRoom', 'CheckRoomId', 'AskOneMessage', 'UpdateRoomInfo', 'GetRoomList', 'JoinRoom', 'PostChat', 'InvalidRoom', 'Empty']
        self.validRoomType = ['chat_room']
        self.validTarget = ['server', 'room_generic', 'host', 'front_end']
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
        if t in self.validType:
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

    def SetUser(self, username):
        self.data['user'] = username
    def GetUser(self):
        return self.data['user']
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
    def GetRoomList(self, roomList):
        return self.data['roomList']
    def SetResult(self, result):
        self.data['result'] = result
    def GetResult(self):
        if self.data['type'] == 'CheckRoomId':
            return self.data['result']
        else:
            raise Exception("Tried to read result when not supposed to")
    def SetUserList(self, userList):
        self.data['userList'] = userList
    def GetUserList(self):
        return self.data['userList']
    def SetMsg(self, msg):
        self.data['msg'] = msg
    def GetMsg(self):
        return self.data['msg']
    # Is functions with Get*()
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

    def IsCreateRoom(self):
        return self.GetType() == 'CreateRoom'
    def IsCheckRoomId(self):
        return self.GetType() == 'CheckRoomId'
    def IsAskOneMessage(self):
        return self.GetType() == 'AskOneMessage'
    def IsGetRoomList(self):
        return self.GetType() == 'GetRoomList'
    def IsJoinRoom(self):
        return self.GetType() == 'JoinRoom'
    def IsPostChat(self):
        return self.GetType() == 'PostChat'
    def IsEmpty(self):
        return self.GetType() == 'Empty'
    def IsToServer(self):
        return self.GetTarget() == 'server'
    def IsToRoom(self):
        return self.GetTarget().startswith('room')
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
    def MakeAskOneMessageRequest(self, roomid, username):
        self.SetRequest()
        self.SetTarget('room_generic')
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
