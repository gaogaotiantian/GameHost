from flask import Flask, render_template, request, make_response, redirect, url_for
import socket
from GameRoom.GameRoomPacket.GRPacket import GRPacket
app = Flask(__name__)

class GameRoomClient:
    def __init__(self, conn = '/home/gaotian/Programs/GameHost/GameRoomConn'):
        self.connected = False
        self.conn = conn
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.conn)
            print 'Connected to conn!'
            sdpkt = GRPacket()
            sdpkt.MakeInitTestRequest()
            print 'Made init packet'
            sock.send(sdpkt.Serialize())
            sock.settimeout(4)
            data = sock.recv(1024)
            rcvpkt = GRPacket(data)
            if rcvpkt.IsSuccess() and rcvpkt.IsInitTest():
                print ("Connected to GameRoom!")
                self.connected = True
            else:
                print ("Error when connecting to GameRoom!")
                self.connected = False
            sock.close()
        except Exception as e:
            print e
            print ("Failed to connect to %s" % conn)
            self.connected = False
    def SendAndRecvPacket(self, sdpkt):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.conn)
        sock.send(sdpkt.Serialize())
        data = sock.recv(4096)
        rcvpkt = GRPacket(data)
        sock.close()
        return rcvpkt

    def CreateRoom(self, username, roomType):
        sdpkt = GRPacket()
        sdpkt.MakeCreateRoomRequest(username, roomType)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        if rcvpkt.IsSuccess():
            return rcvpkt.GetRoomId()
        else:
            return None
    def JoinRoom(self, username, roomid):
        sdpkt = GRPacket()
        sdpkt.MakeJoinRoomRequest(username, roomid)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        return rcvpkt.IsSuccess()

    def HasRoom(self, roomid):
        sdpkt = GRPacket()
        sdpkt.MakeHasRoomRequest(roomid)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        if rcvpkt.IsSuccess():
            return rcvpkt.GetResult()
        else:
            return False
    def GetRoomInfo(self, roomid):
        sdpkt=GRPacket()
        sdpkt.MakeGetRoomInfoRequest(roomid)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        return rcvpkt
    def AskOneMsg(self, roomid, username, target):
        sdpkt = GRPacket()
        sdpkt.MakeAskOneMessageRequest(roomid, username, target)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        return rcvpkt
    def GetRoomList(self):
        sdpkt = GRPacket()
        sdpkt.MakeGetRoomListRequest()
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        return rcvpkt
    def LeaveRoom(self, roomid, username):
        sdpkt = GRPacket()
        sdpkt.MakeLeaveRoomRequest(roomid, username)
        return self.SendAndRecvPacket(sdpkt)
    def KickUserList(self, roomid, userList):
        sdpkt = GRPacket()
        sdpkt.MakeKickUserListRequest(roomid, userList)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        return rcvpkt
    def PostChat(self, roomid, username, msg):
        sdpkt = GRPacket()
        sdpkt.MakePostChatRequest(roomid, username, msg)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        return rcvpkt
    def GameExist(self, roomid):
        sdpkt = GRPacket()
        sdpkt.MakeGameExistRequest(roomid)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        if rcvpkt.IsSuccess():
            return rcvpkt.GetResult()
        else:
            return False
    def StartGame(self, roomid, userList):
        sdpkt = GRPacket()
        sdpkt.MakeStartGameRequest(roomid, userList)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        return rcvpkt
    def GetGameInfo(self, roomid, target):
        sdpkt = GRPacket()
        sdpkt.MakeGetGameInfoRequest(roomid, target)
        return self.SendAndRecvPacket(sdpkt)
    def GomokuMove(self, roomid, username, x, y):
        sdpkt = GRPacket()
        sdpkt.MakeGomokuMoveRequest(roomid, username, x, y)
        return self.SendAndRecvPacket(sdpkt)


        

gameRoom = GameRoomClient()

@app.route('/')
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    username = request.cookies.get('username')
    resp = make_response(render_template('index.html', username=username, action_url = url_for('action')))
    if request.method == 'POST':
        username = request.form['username'] 
        if username is not None:
            resp = make_response(render_template('index.html', username=username, action_url = url_for('action')))
            resp.set_cookie('username', username)
        else:
            print "Error!"
            resp = make_response('Error!')
    return resp
@app.route('/action', methods=['GET', 'POST'])
def action():
    username = request.cookies.get('username')
    print request.form
    if 'roomid' in request.form:
        roomid = request.form['roomid']
    if request.method == 'POST':
        if request.form['action'] == 'AskOneMsg':
            target = request.form['target']
            return gameRoom.AskOneMsg(roomid, username, target).Serialize()
        if request.form['action'] == 'GetRoomInfo':
            return gameRoom.GetRoomInfo(roomid)
        if request.form['action'] == 'GetRoomList':
            return gameRoom.GetRoomList().Serialize()
        if request.form['action'] == 'LeaveRoom':
            return gameRoom.LeaveRoom(roomid, username).Serialize()
        if request.form['action'] == 'KickUserList':
            userList = request.form.getlist('userList[]');
            return gameRoom.KickUserList(roomid, userList).Serialize()
        if request.form['action'] == 'PostChat':
            msg = request.form['message']
            return gameRoom.PostChat(roomid = roomid, username = username, msg = msg).Serialize()
        if request.form['action'] == 'StartGame':
            userList = request.form.getlist('userList[]');
            return gameRoom.StartGame(roomid, userList).Serialize()
        if request.form['action'] == 'GetGameInfo':
            target = request.form['target']
            return gameRoom.GetGameInfo(roomid, target).Serialize()
        # Gomoku Specific Action
        if request.form['action'] == 'GomokuMove':
            x = request.form['x']
            y = request.form['y']
            return gameRoom.GomokuMove(roomid, username, x, y).Serialize()




@app.route('/room/<roomid>/game')
def game(roomid):
    username = request.cookies.get('username')
    if username == '' or username == None or not gameRoom.HasRoom(roomid):
        return 'Invalid username or roomid!'
    else:
        roomList = gameRoom.GetRoomList().GetRoomList()
        roomInfo = roomList[roomid]
        roomType = roomInfo['roomType']
        if roomType == 'gomoku_room':
            return render_template('gomoku.html', roomid = roomid, action_url = url_for('action'))
        else:
            return ''

@app.route('/room/<roomid>')
def room(roomid):
    username = request.cookies.get('username')
    if username == '' or username == None:
        return 'You need to have a username to join room!'
    else:
        if gameRoom.HasRoom(roomid):
            if gameRoom.JoinRoom(username, roomid):
                return render_template('room.html', roomid = roomid, action_url = url_for('action'), index_url = url_for('index'), game_url = url_for('game', roomid = roomid))
            
    return 'No Such Room!'

@app.route('/create_room', methods=['GET', 'POST'])
def create_room():
    username = request.cookies.get('username')
    print username
    if request.method == 'POST':
        if username == '' or username == None:
            return 'You need to have a username to create room!'
        else:
            roomType = request.form['room_type']
            roomid = gameRoom.CreateRoom(username, roomType)
            if roomid == None:
                return 'Create room failed!'
            else:
                return redirect(url_for('room', roomid = roomid))
    else:
        return 'You are not supposed to open this page by your own!'
    
@app.route('/join_room', methods=['POST'])
def join_room():
    username = request.cookies.get('username')
    if request.method == 'POST':
        if username == '' or username == None:
            return 'You need to have a username to create room!'
        else:
            roomid = request.form['roomid']
            return redirect(url_for('room', roomid = roomid))

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='192.168.0.25')
