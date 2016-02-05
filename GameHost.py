from flask import Flask, render_template, request, make_response, redirect, url_for
import socket
from GameRoom.GameRoomPacket.GRPacket import GRPacket
app = Flask(__name__)

class GameRoomClient:
    def __init__(self, conn = '/tmp/GameRoomConn'):
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
        data = sock.recv(1024)
        rcvpkt = GRPacket(data)
        sock.close()
        return rcvpkt

    def CreateRoom(self, username, roomType):
        sdpkt = GRPacket()
        sdpkt.MakeCreateRoomRequest(username, roomType)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        if rcvpkt.IsSuccess():
            print rcvpkt.Serialize()
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
            return Fail
    def GetRoomInfo(self, roomid):
        sdpkt=GRPacket()
        sdpkt.MakeGetRoomInfoRequest(roomid)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        return rcvpkt
    def AskOneMsg(self, roomid, username):
        sdpkt = GRPacket()
        sdpkt.MakeAskOneMessageRequest(roomid, username)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        return rcvpkt
    def GetRoomList(self):
        sdpkt = GRPacket()
        sdpkt.MakeGetRoomListRequest()
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        return rcvpkt
    def PostChat(self, roomid, username, msg):
        sdpkt = GRPacket()
        sdpkt.MakePostChatRequest(roomid, username, msg)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        return rcvpkt
        

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
    if request.method == 'POST':
        if request.form['action'] == 'AskOneMsg':
            roomid = request.form['roomid']
            return gameRoom.AskOneMsg(roomid, username).Serialize()
        if request.form['action'] == 'GetRoomInfo':
            roomid = request.form['roomid']
            return gameRoom.GetRoomInfo(roomid)
        if request.form['action'] == 'GetRoomList':
            return gameRoom.GetRoomList().Serialize()
        if request.form['action'] == 'PostChat':
            print 'PostChat!'
            roomid = request.form['roomid']
            msg = request.form['message']
            return gameRoom.PostChat(roomid = roomid, username = username, msg = msg).Serialize()

@app.route('/room/<roomid>')
def room(roomid):
    username = request.cookies.get('username')
    if username == '' or username == None:
        return 'You need to have a username to join room!'
    else:
        if gameRoom.HasRoom(roomid):
            if gameRoom.JoinRoom(username, roomid):
                return render_template('room.html', roomid = roomid, action_url = url_for('action'), index_url = url_for('index'))
            
    return 'No Such Room!'

@app.route('/create_room', methods=['GET', 'POST'])
def create_room():
    username = request.cookies.get('username')
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
    app.run(debug=True, host='192.168.0.25')
