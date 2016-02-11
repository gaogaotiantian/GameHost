import random
from GameRoomPacket.GRPacket import GRPacket
from User import User
class Gomoku:
    def __init__(self, playerList, userList, maxWidth = 15, maxLength = 15):
        self.blackUser = ""
        self.blackRestart = False
        self.whiteUser = ""
        self.whiteRestart = False
        self.maxWidth = maxWidth
        self.maxLength = maxLength
        self.moveColor = 'Black'
        self.playerList = list(playerList)
        self.userList = userList
        self.board = [[0]*maxWidth for i in range(maxLength)]
        self.valid = False
        self.done = False
        self.winner = ''
        self.gameInfo = {}
    def InitBoard(self):
        self.winner = ''
        self.moveColor = 'Black'
        self.board = [[0]*self.maxWidth for i in range(self.maxLength)]
        if random.randint(0,1) == 0:
            self.blackUser = self.playerList[0]
            self.whiteUser = self.playerList[1]
        else:
            self.blackUser = self.playerList[1]
            self.whiteUser = self.playerList[0]
        self.UpdateGameInfo()
    def SendPktToEveryone(self, pkt):
        for user in self.userList.itervalues():
            user.AddMsg(pkt, 'Gomoku')
    def GetOneMsg(self, username):
        if username in self.userList:
            return self.userList[username].GetMsg('Gomoku')
        else:
            return GRPacket('GR_INVALIDROOM')
    def GenGomokuInfoMsg(self):
        pkt = GRPacket()
        pkt.MakeGomokuInfoRespond(gameInfo = self.gameInfo)
        self.SendPktToEveryone(pkt)
    def UpdateGameInfo(self):
        self.gameInfo['playerList'] = [self.blackUser, self.whiteUser]
        self.gameInfo['userList'] = self.userList.keys()
        self.gameInfo['board'] = self.board
        self.gameInfo['moveColor'] = self.moveColor
        self.gameInfo['winner'] = self.winner
        self.GenGomokuInfoMsg()
        
    def StartGame(self, playerList):
        self.playerList = list(playerList)
        self.InitBoard()

    def Restart(self, username):
        if username == self.blackUser:
            self.blackRestart = True
        elif username == self.whiteUser:
            self.whiteRestart = True
        if self.blackRestart and self.whiteRestart:
            self.InitBoard()
            self.GenGomokuInfoMsg()
        return GRPacket('GR_SUCCESS')

    def ParsePacket(self, rcvpkt):
        assert rcvpkt.IsToGomoku()
        if rcvpkt.IsType('AskOneMessage'):
            username = rcvpkt.GetUser()
            return self.GetOneMsg(username)
        elif rcvpkt.IsType('GetGameInfo'):
            self.UpdateGameInfo()
            return GRPacket('GR_SUCCESS')
        elif rcvpkt.IsType('GomokuMove'):
            username = rcvpkt.GetUser()
            x = int(rcvpkt.GetData('x'))
            y = int(rcvpkt.GetData('y'))
            return self.Move(username, x, y)
        elif rcvpkt.IsType('GomokuRestart'):
            username = rcvpkt.GetUser()
            return self.Restart(username)
        else:
            return GRPacket('GR_FAIL')

    # Game related functions
    def CheckWin(self, colorNum, x, y):
        # colorNum = 1 : Black
        # colorNum = 2 : White
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for d in directions:
            conti = 0
            point = [x - 4*d[0], y - 4*d[1]]
            for i in range(9):
                try:
                    if self.board[point[0]+i*d[0]][point[1]+i*d[1]] == colorNum:
                        conti = conti + 1
                        if conti == 5:
                            return True
                    else:
                        conti = 0
                except IndexError:
                    conti = 0
        return False
    def Move(self, username, x, y):
        if self.winner == '' and x >= 0 and x < self.maxWidth and y >= 0 and y < self.maxLength and self.board[x][y] == 0:
            if username == self.blackUser and self.moveColor == 'Black':
                self.board[x][y] = 1
                self.moveColor = 'White'
                if self.CheckWin(1, x, y):
                    self.winner = 'Black'
                self.UpdateGameInfo();
                return GRPacket('GR_SUCCESS')
            if username == self.whiteUser and self.moveColor == 'White':
                self.board[x][y] = 2
                self.moveColor = 'Black'
                if self.CheckWin(2, x, y):
                    self.winner = 'White'
                self.UpdateGameInfo();
                return GRPacket('GR_SUCCESS')
        return GRPacket('GR_FAIL')

if __name__ == '__main__':
    testGomoku = Gomoku(['black', 'white'], {})
    testGomoku.blackUser = 'black'
    testGomoku.whiteUser = 'white'
    testGomoku.Move('black', 5, 5)
