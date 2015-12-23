import sublime, sublime_plugin
from qpython import qconnection
from qpython.qtype import QException
from socket import error as socket_error

class QCon():
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.q = qconnection.QConnection(host = self.host, port = self.port, username = self.username, password = self.password)

    @classmethod
    def fromDict(cls, d):
        if d is None: return None
        return cls(d["host"], d["port"], d["username"], d["password"])

    @classmethod
    def fromH(cls, h):
        if h is None: return None
        p = h.split(':')
        for i in range(len(p), 4):
            p.append(None)
        if not p[1].isdigit(): 
            sublime.error_message('port must be digit: ' + p[1])
            raise Exception('port must be digit: ' + p[1])

        return cls(p[0], int(p[1]), p[2], p[3])

    @classmethod
    def loadFromView(cls, view):
        h = view.settings().get('q_handle')
        return QCon.fromH(h)

    def saveToView(self, view):
        view.settings().set('q_handle', self.h())

    def toDict(self):
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password
        }

    def h(self):
        #return '{0}:{1}:{2}:{3}'.format(self.host, self.port, self.username, self.password)
        s = self.host + ':' + str(self.port)
        if self.username: s+= ':' + self.username
        if self.password: s+= ':' + self.password
        print(s)
        return s

    def status(self):
        status = 'OK' if self.ok() else 'FAIL'
        return status + ': ' + self.h()

    def ok(self):
        try:
            self.q.open()
            self.ok = True
        except socket_error as serr:
            self.ok = False
            return False
        finally:
            self.q.close()
        return True