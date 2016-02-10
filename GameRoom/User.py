import time
import json
from GameRoomPacket.GRPacket import GRPacket
class User:
    def __init__(self, username):
        self.lastActivate = time.time()
        self.username = username
        self.msgList = []
        self.msgGomokuList = []
    def __repr__(self):
        return json.dumps(self.username)
    def AddMsg(self, pkt, target = 'General'):
        if target == 'General':
            self.msgList.append(pkt)
        elif target == 'Gomoku':
            self.msgGomokuList.append(pkt)

    def GetMsg(self, target = 'General'):
        self.Refresh()
        if target == 'General':
            if len(self.msgList) == 0:
                return GRPacket('GR_EMPTY')
            else:
                return self.msgList.pop(0)
        elif target == 'Gomoku':
            if len(self.msgGomokuList) == 0:
                return GRPacket('GR_EMPTY')
            else:
                return self.msgGomokuList.pop(0)
        return GRPacket('GR_FAIL')
    def Refresh(self):
        self.lastActivate = time.time()
    def CheckTimeInterval(self, interval):
        return time.time() - self.lastActivate > interval
