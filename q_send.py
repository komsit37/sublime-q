import sublime
import sublime_plugin

from .qpython.qtype import QException
from socket import error as socket_error
import numpy
import datetime

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
        con = Q.QCon.loadFromViewWithPrompt(self.view)
        if con:
            return self.send(con, input)

    #keep this because it is overwritten in QUpdateCompletionsCommand
    def send(self, con, input):
        return QSendRawCommand.sendAndUpdateStatus(self.view, con, input)

    @staticmethod
    def sendAndUpdateStatus(view, con, input):
        view.set_status('result', 'executing...')
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

            input_prefix = input[:5] # probably .Q.s or .j.j -- make more generic later if necessary
            input_body = input[5:]

            mem_query = '@[{.Q.w[][`used]};();0]'
            write_query = '@[{`.st.tmp set x;`sublimeq};();0b]'
            initial_query = '(' + mem_query + ';' + write_query + ')'

            pre_res = q(initial_query)

            try:
                write_flag = util.decode(pre_res[1]) == 'sublimeq'
                start_mem = int(util.decode(pre_res[0]))
            except:
                write_flag = False
                start_mem = 0

            input =  input_prefix + ('.st.tmp:' if write_flag else '') + input_body

            start_time = datetime.datetime.now()
            res = util.decode(q(input))
            end_time = datetime.datetime.now()
            time = str(end_time - start_time)[2:-3]

            dims_query = '$[@[{`tmp in key x};`.st;0b];" x " sv string (count @[{$[0<=type x; cols x;()]};.st.tmp;()]),count .st.tmp;0]'
            post_query = '(' + mem_query + ';' + dims_query + ')'
            post_res = q(post_query)

            try:
                end_mem = int(util.decode(post_res[0]))
                mem = end_mem - start_mem
                sign = '+' if mem>0 else '-'
                mem = util.format_mem(abs(mem))
                dims = util.decode(post_res[1])
            except:
                sign = ''
                mem = '0'
                dims = '0'

            # Return input itself if no results return (e.g. a query that defines a variable or function)
            # if res in [None, 'None']:
            #     res = input_body

            status = 'Result: ' + dims + ', ' + time + ', ' + sign + mem
            #self.view.set_status('result', 'Result: ' + count + ', ' + time + ', ' + sign + mem)
        except QException as e:
            res = "error: `" + util.decode(e)
            status = "error: `" + util.decode(e)
        except socket_error as serr:
            msg = 'Sublime-q cannot to connect to \n"' + con.h() + '"\n\nError message: ' + str(serr)
            sublime.error_message(msg)
            res = ""
            status = "error: " + str(serr)
        finally:
            q.close()

        #self.view.set_status('q', con.status())
        return {'result': res, 'status': status}

class QSendCommand(QSendRawCommand):
    def do(self, edit=None, input=None):
        if (input[0] == "\\"):
            input = "value\"\\" + input + "\""

        input = ".Q.s " + input
        return super().do(input=input)

class QSendJsonCommand(QSendRawCommand):
    def do(self, edit=None, input=None):
        if (input[0] == "\\"):
            input = "value\"\\" + input + "\""

        input = ".j.j " + input  #save to temprary result, so we can get dimension later
        return super().do(input=input)
