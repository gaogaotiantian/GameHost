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
            sdpkt = GRPacket()
            sdpkt.MakeInitTestRequest()
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
            #self.sock.close()
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

    def CreateRoom(self, username):
        sdpkt = GRPacket()
        sdpkt.MakeCreateRoomRequest(username)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        if rcvpkt.IsSuccess():
            print rcvpkt.Serialize()
            return rcvpkt.GetRoomId()
        else:
            return 'Fail'
    def HasRoom(self, roomid):
        sdpkt = GRPacket()
        sdpkt.MakeHasRoomRequest(roomid)
        rcvpkt = self.SendAndRecvPacket(sdpkt)
        if rcvpkt.IsSuccess():
            return rcvpkt.GetResult()
        else:
            return Fail
        

gameRoom = GameRoomClient()

@app.route('/')
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    username = request.cookies.get('username')
    resp = make_response(render_template('index.html', username=username))
    if request.method == 'POST':
        username = request.form['username'] 
        if username is not None:
            resp = make_response(render_template('index.html', username=username))
            resp.set_cookie('username', username)
        else:
            print "Error!"
            resp = make_response('Error!')
    return resp
@app.route('/room/<roomid>')
def room(roomid):
    if gameRoom.HasRoom(roomid):
        return 'Hello world' + roomid
    else:
        return 'No Such Room!'

@app.route('/create_room.html')
def create_room():
    username = request.cookies.get('username')
    if username == '' or username == None:
        return 'You need to have a username!'
    else:
        roomid = gameRoom.CreateRoom(username)
        if roomid == 'Fail':
            return 'Create room failed!'
        else:
            return redirect(url_for('room', roomid = roomid))
if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.25')
