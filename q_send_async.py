import sublime
import sublime_plugin
from . import QCon
from . import q_send
from . import q_select_text

#run q statement in an alternative thread using sublime.set_timeout_async
#see https://forum.sublimetext.com/t/how-to-run-part-of-my-plugin-in-the-second-thread-properly/18962/7
#and https://www.sublimetext.com/docs/3/api_reference.html
class QSendAsyncCommand(sublime_plugin.TextCommand):

    def run(self, edit, output=None):
      s = q_select_text.QSelectTextCommand.selectText(self.view)
      con = QCon.QCon.loadFromViewWithPrompt(self.view)
      if con:
        #do nothing if text is empty
        if s != "":
          sublime.set_timeout_async(lambda: self.send(con, s, output), 0)

    def send(self, con, s, output):
      #print(con.toDict())
      #print(s)
      if (s[0] == "\\"):
        s = "value\"\\" + s + "\""
      s = ".Q.s .st.tmp:" + s  #save to temprary result, so we can get dimension later

      res = q_send.QSendRawCommand.sendAndUpdateStatus(self.view, con, s)
      if output:
        self.view.run_command(output, {"input": res})
      sublime.set_timeout_async(lambda: self.view.run_command("q_update_completions"), 0)


