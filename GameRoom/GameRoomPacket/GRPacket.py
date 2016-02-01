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
        if data == '':
            self.data = {}
            self.data['status'] = 'Success'
            self.data['direction'] = ''
            self.data['type'] = ''
            self.data['user'] = ''
            self.data['roomid'] = ''
            self.validType = ['InitTest', 'CreateRoom', 'CheckRoomId']
        else:
            self.Deserialize(data)
    def SetSuccess(self):
        self.data['status'] = 'Success'
    def SetFail(self):
        self.data['status'] = 'Fail'
    def IsSuccess(self):
        return self.data['status'] == 'Success'
    def IsFail(self):
        return self.data['status'] == 'Fail'

    def SetRequest(self):
        self.data['direction'] = 'Request'
    def SetRespond(self):
        self.data['direction'] = 'Respond'
    def IsRequest(self):
        return self.data['direction'] == 'Request'
    def IsRespond(self):
        return self.data['direction'] == 'Respond'

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
    def IsInitTest(self):
        return self.GetType() == 'InitTest'
    def IsCreateRoom(self):
        return self.GetType() == 'CreateRoom'
    def IsCheckRoomId(self):
        return self.GetType() == 'CheckRoomId'
    def SetUser(self, username):
        self.data['user'] = username
    def GetUser(self):
        if self.data['type'] == 'CreateRoom':
            return self.data['user']
        else:
            raise Exception("Can't get user!")
    def SetRoomId(self, roomid):
        self.data['roomid'] = roomid
    def GetRoomId(self):
        if self.data['type'] == 'CreateRoom' or self.data['type'] == 'CheckRoomId':
            return self.data['roomid']
        else:
            raise Exception("Tried to read roomid when not Creating the room")
    def SetResult(self, result):
        self.data['result'] = result
    def GetResult(self):
        if self.data['type'] == 'CheckRoomId':
            return self.data['result']
        else:
            raise Exception("Tried to read result when not supposed to")
    def MakeInitTestRequest(self):
        self.SetSuccess()
        self.SetRequest()
        self.SetType('InitTest')
    def MakeInitTestResponse(self):
        self.SetSuccess()
        self.SetRespond()
        self.SetType('InitTest')
    def MakeCreateRoomRequest(self, username):
        self.SetRequest()
        self.SetType('CreateRoom')
        self.SetUser(username)
    def MakeCreateRoomResponse(self, username, roomid):
        self.SetSuccess()
        self.SetRespond()
        self.SetType('CreateRoom')
        self.SetUser(username)
        self.SetRoomId(roomid)
    def MakeHasRoomRequest(self, roomid):
        self.SetRequest()
        self.SetType('CheckRoomId')
        self.SetRoomId(roomid)
    def MakeHasRoomResponse(self, roomid, result):
        self.SetRespond()
        self.SetType('CheckRoomId')
        self.SetRoomId(roomid)
        self.SetResult(result)
    def MakeFailResponse(self):
        self.SetFail()
        self.SetRespond()
    def Serialize(self):
        return json.dumps(self.data)
    def Deserialize(self, data):
        self.data = json.loads(data)
