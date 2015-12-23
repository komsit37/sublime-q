import sublime
import sublime_plugin

from qpython import qconnection
from qpython.qtype import QException
from socket import error as socket_error

from . import chain
from . import QCon as Q

#for testing in console
#from qpython import qconnection
#q = qconnection.QConnection(host = 'localhost', port = 5555)
#q.open()
#d = q('.Q.s `a`b`c!1 2 3')
#d = d.decode('utf-8')
#view.show_popup(d)
class QSendRawCommand(chain.ChainCommand):

    def do(self, edit=None, input=None):
        con = Q.QCon.loadFromView(self.view)
        print()
        if con:
            return self.send(con, input)
        else:
            print('connect first!')
   
    def send(self, con, s):
        try:
            q = con.q
            q.open()
            self.view.set_status('q', 'OK: ' + con.h())
            
            #bundle all pre/post q call to save round trip time
            pre_exec = []
            #pre_exec.append('if[not `st in key `; .st.tmp: `]')
            pre_exec.append('.st.start:.z.T')   #start timing
            pre_exec = ';'.join(pre_exec)
            #print(pre_exec)
            q(pre_exec)

            res = q(s)
           
            post_exec = []
            #get exec time, result dimensions
            post_exec.append('res:`time`c!((3_string `second$.st.execTime:.z.T-.st.start);(" x " sv string (count @[cols;.st.tmp;()]),count .st.tmp))')
            post_exec.append('delete tmp, start, execTime from `.st') #clean up .st
            post_exec.append('.st: ` _ .st') #clean up .st
            post_exec.append('res')
            post_exec = ';'.join(post_exec)
            post_exec = '{' + post_exec + '}[]'   #exec in closure so we don't leave anything behind
            #print(post_exec)
            tc = q(post_exec)

            res = self.decode(res)
            time = self.decode(tc[b'time'])
            count = self.decode(tc[b'c'])
            #print(res)
            self.view.set_status('result', 'Result: ' + count + ', ' + time)
        except QException as e:
            res = "error: `" + self.decode(e)
        except socket_error as serr:
            sublime.error_message('Sublime-q cannot to connect to \n"' + con.h() + '"\n\nError message: ' + str(serr))
            self.view.set_status('q', 'FAIL: ' + con.h())
            raise serr
        finally:
            q.close()
        
        #return itself if query is define variable or function
        if res is None:
            res = s
        return res

    def decode(self, s):
        if type(s) is bytes:
            return s.decode('utf-8')
        elif type(s) is QException:
            return str(s)[2:-1] #extract error from b'xxx'
        else:
            return str(s)

class QSendCommand(QSendRawCommand):
    def do(self, edit=None, input=None):
        if (input[0] == "\\"):
            input = "value\"\\" + input + "\""
        else:
            input = ".Q.s .st.tmp:" + input  #save to temprary result, so we can get dimension later
        return super().do(input=input)

class QSendJsonCommand(QSendRawCommand):
    def do(self, edit=None, input=None):
        if (input[0] == "\\"):
            input = "value\"\\" + input + "\""
        else:
            input = ".j.j .st.tmp:" + input  #save to temprary result, so we can get dimension later
        return super().do(input=input)

class QSendTypeCommand(QSendCommand):
    def do(self, edit=None, input=None):
        input = "{$[.Q.qt x;meta x;100h=type x;value x;.Q.ty each x]} " + input
        return super().do(input=input)

class QSendEnvCommand(QSendCommand):
    def do(self, edit=None, input=None):
        input = '((enlist `ns)!(enlist(key `) except `q`Q`h`j`o)),{(`$/:x )! system each x } \"dvabf\"'
        return super().do(input=input)

class QSendMemCommand(QSendCommand):
    def do(self, edit=None, input=None):
        input = '.Q.w[]'
        return super().do(input=input)

class QSendTableCommand(QSendCommand):
    def do(self, edit=None, input=None):
        input = '(tables `.)!cols each tables `.'
        return super().do(input=input)
