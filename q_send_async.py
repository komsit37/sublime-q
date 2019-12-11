import sublime
import sublime_plugin
from . import QCon
from . import q_send
from . import q_select_text

#run q statement in an alternative thread using sublime.set_timeout_async
#see https://forum.sublimetext.com/t/how-to-run-part-of-my-plugin-in-the-second-thread-properly/18962/7
#and https://www.sublimetext.com/docs/3/api_reference.html
class QSendAsyncCommand(sublime_plugin.TextCommand):

    def run(self, edit, input=None, chain=None):
      s = q_select_text.QSelectTextCommand.selectText(self.view)
      con = QCon.QCon.loadFromView(self.view)
      if con:
        #do nothing if text is empty
        if s != "":
          sublime.set_timeout_async(lambda: self.send(con, s), 0)
      else:
        #connect first
        sublime.message_dialog('Sublime-q: Choose your q connection first!')
        self.view.window().run_command('q_show_connection_list')

    def send(self, con, s):
      #print(con.toDict())
      #print(s)
      if (s[0] == "\\"):
        s = "value\"\\" + s + "\""
      s = ".Q.s .st.tmp:" + s  #save to temprary result, so we can get dimension later

      res = q_send.QSendRawCommand.sendAndUpdateStatus(self.view, con, s)
      self.view.run_command("q_out_panel", {"input": res})
      sublime.set_timeout_async(lambda: self.view.run_command("q_update_completions"), 0)


