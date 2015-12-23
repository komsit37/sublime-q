import sublime
import sublime_plugin

from qpython import qconnection
from qpython.qtype import QException
from socket import error as socket_error

from . import chain


class QSendCommand(chain.ChainCommand):
    def do(self, edit, input=None):
        return self.send(input)
   
    def send(self, s):
        try:
            q = qconnection.QConnection(host = 'localhost', port = 5555)
            q.open()
            self.view.set_status('q', 'OK')

            statement = self.transfrom(s)
            
            #bundle all pre/post q call to save round trip time
            pre_cmds = []
            #pre_cmds.append('if[not `st in key `; .st.tmp: `]')
            pre_cmds.append('.st.start:.z.T')   #start timing
            pre_cmd_statement = ';'.join(pre_cmds)
            #print(pre_cmd_statement)
            q(pre_cmd_statement)

            res = q(statement)
           
            post_cmds = []
            #get exec time, result dimensions
            post_cmds.append('res:`time`c!((3_string `second$.st.execTime:.z.T-.st.start);(" x " sv string (count @[cols;.st.tmp;()]),count .st.tmp))')
            post_cmds.append('delete tmp, start, execTime from `.st') #clean up .st
            post_cmds.append('.st: ` _ .st') #clean up .st
            post_cmds.append('res')
            post_cmd_statement = ';'.join(post_cmds)
            post_cmd_statement = '{' + post_cmd_statement + '}[]'   #exec in closure so we don't leave anything behind
            #print(post_cmd_statement)
            tc = q(post_cmd_statement)

            res = self.decode(res)
            time = self.decode(tc[b'time'])
            count = self.decode(tc[b'c'])
            #print(res)
            self.view.set_status('result', 'Result: ' + count + ', ' + time)
        except QException as e:
            res = "error: `" + self.decode(e)
        except socket_error as serr:
            self.view.set_status('q', 'FAIL: ' + Q.con)
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

    def transfrom(self, s):
        if (s[0] == "\\"):
            return "value\"\\" + s + "\""
        else:
            return ".Q.s .st.tmp:" + s  #save to temprary result, so we can get dimension later
