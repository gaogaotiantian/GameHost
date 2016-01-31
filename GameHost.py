from flask import Flask, render_template, request, make_response
import socket
app = Flask(__name__)

class GameRoomClient:
    def __init__(self, conn = '/tmp/GameRoomConn'):
        self.connected = False
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(conn)
            self.sock.send('Initial connection test')
            self.sock.settimeout(2)
            data = self.sock.recv(1024)
            if data == 'Ready':
                print ("Connected to GameRoom!")
                self.connected = True
            else:
                print ("Error when connecting to GameRoom!")
                self.connected = False
        except Exception as e:
            print ("Failed to connect to %s" % conn)
            self.connected = False


gameRoom = GameRoomClient()
room = 1

@app.route('/')
@app.route('/index.html', methods=['GET', 'POST'])
def hello_world():
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
if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.25')
