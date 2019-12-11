import sublime
import sublime_plugin

from .qpython.qtype import QException
from socket import error as socket_error
import numpy

from . import q_chain
from . import QCon as Q
from . import util

#for testing in console
#from qpython import qconnection
#q = qconnection.QConnection(host = 'localhost', port = 5555)
#q.open()
#d = q('.Q.s `a`b`c!1 2 3')
#d = d.decode('utf-8')
#view.show_popup(d)
class QSendRawCommand(q_chain.QChainCommand):

    def do(self, edit=None, input=None):
        con = Q.QCon.loadFromView(self.view)
        if con:
            return self.send(con, input)
        else:
            #connect first
            sublime.message_dialog('Sublime-q: Choose your q connection first!')
            self.view.window().run_command('show_connection_list')

    #keep this because it is overwritten in QUpdateCompletionsCommand
    def send(self, con, input):
      return QSendRawCommand.sendAndUpdateStatus(self.view, con, input)

    @staticmethod
    def sendAndUpdateStatus(view, con, input):
      view.set_status('result', 'excuting...')
      try:
        d = QSendRawCommand.executeRaw(con, input)
        view.set_status('result', d['status'])
        view.set_status('q', con.status())
        return d['result']
      except Exception as e:
        sublime.error_message('Error in QSendRawCommand.sendAndUpdateStatus:\n' + str(e))
        view.set_status('result', 'ERROR')
        view.set_status('q', con.status())
        raise e

    @staticmethod
    def executeRaw(con, input):
      try:
          q = con.q
          q.open()

          #bundle all pre/post q call to save round trip time
          pre_exec = []
          #pre_exec.append('if[not `st in key `; .st.tmp: `]')
          pre_exec.append('.st.start:.z.T')   #start timing
          pre_exec.append('.st.mem: @[{.Q.w[][`used]}; (); 0]')   #start timing
          pre_exec = ';'.join(pre_exec)
          #print(pre_exec)
          q(pre_exec)

          res = q(input)

          post_exec = []
          #get exec time, result dimensions
          post_exec.append('res:`time`c`mem!((3_string `second$.st.execTime:.z.T-.st.start);(" x " sv string (count @[{$[0<=type x; cols x;()]};.st.tmp;()]),count .st.tmp); ((@[{.Q.w[][`used]}; (); 0]) - .st.mem))')
          #post_exec.append('delete tmp, start, execTime from `.st') #clean up .st
          post_exec.append('delete start, execTime from `.st') #clean up .st but keep tmp result, so we can use it to plot if needed
          #post_exec.append('.st: ` _ .st') #clean up .st
          post_exec.append('res')
          post_exec = ';'.join(post_exec)
          post_exec = '{' + post_exec + '}[]'   #exec in closure so we don't leave anything behind
          #print(post_exec)
          tc = q(post_exec)

          res = QSendRawCommand.decode(res)
          time = QSendRawCommand.decode(tc[b'time'])
          count = QSendRawCommand.decode(tc[b'c'])
          mem = QSendRawCommand.decode(tc[b'mem'])
          mem = int(mem)
          sign = '+' if mem>0 else '-'
          mem = util.format_mem(abs(int(mem)))

          #return input itself if query is define variable or function (and return no result)
          if res is None:
            res = input

          status = 'Result: ' + count + ', ' + time + ', ' + sign + mem
          #self.view.set_status('result', 'Result: ' + count + ', ' + time + ', ' + sign + mem)
      except QException as e:
          res = "error: `" + QSendRawCommand.decode(e)
          status = "error: `" + QSendRawCommand.decode(e)
      except socket_error as serr:
          sublime.error_message('Sublime-q cannot to connect to \n"' + con.h() + '"\n\nError message: ' + str(serr))
          raise serr
      finally:
          q.close()

      #self.view.set_status('q', con.status())

      return {'result': res, 'status': status}

    @staticmethod
    def decode(s):
        if type(s) is bytes or type(s) is numpy.bytes_:
            return s.decode('utf-8')
        elif type(s) is QException:
            return str(s)[2:-1] #extract error from b'xxx'
        else:
            return str(s)

class QSendCommand(QSendRawCommand):
    def do(self, edit=None, input=None):
        if (input[0] == "\\"):
            input = "value\"\\" + input + "\""

        input = ".Q.s .st.tmp:" + input  #save to temprary result, so we can get dimension later
        return super().do(input=input)

class QSendJsonCommand(QSendRawCommand):
    def do(self, edit=None, input=None):
        if (input[0] == "\\"):
            input = "value\"\\" + input + "\""

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
