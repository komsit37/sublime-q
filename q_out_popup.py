from . import q_chain
import sublime
import styled_popup
#from qpython import qconnection
#q = qconnection.QConnection(host = 'localhost', port = 5555)
#q.open()
#d = q('.j.j `a`b`c!1 2 3')
#d = d.decode('utf-8')
#view.show_popup(d)

#http://www.sublimetext.com/forum/viewtopic.php?__s=hw11owwz1ppf7twtyaxo&f=2&t=17583
#https://github.com/huot25/StyledPopup
#this is a mess because we need to wait for old pop un to close
#can only show one popup at a time
class QOutPopupBaseCommand(q_chain.QChainCommand):
	TO_CLOSE = False
	ACTUALLY_CLOSED = True

	def do(self, edit=None, input=None):
		#print(input)
		template = '<a href="close" style="display:inline;color:green;">x</a> {0}'
		self.html = template.format(input)

		if QOutPopupBaseCommand.ACTUALLY_CLOSED:
			current = self.current_rowcol()
			self.rowcol = self.current_rowcol()
			self.rowcol = [max(0, self.rowcol[0] - 2), self.rowcol[1] + 10]
			self.to_rowcol(self.rowcol)
			styled_popup.show_popup(self.view, self.html,on_hide=self.on_hide, on_navigate=self.on_navigate)
			self.to_rowcol(current)
			QOutPopupBaseCommand.TO_CLOSE = True
			QOutPopupBaseCommand.ACTUALLY_CLOSED = False
		else:
			print('close old popup first')
			QOutPopupBaseCommand.TO_CLOSE = False
			self.view.hide_popup()
			#wait until previous popup close and then open again
			#press same shortcut to hide popup
			#sublime.set_timeout(lambda x=input:self.do(input=x), 100)
		return ''	#return something so that the q_chain can continue

	def eol_rowcol(self):
		return self.view.rowcol(self.view.line(self.view.sel()[0]).end())

	def current_rowcol(self):
		return self.view.rowcol(self.view.sel()[0].end())

	def to_rowcol(self, rowcol):
		pt = self.view.text_point(rowcol[0], rowcol[1])
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(pt))

	def on_hide(self):
		if QOutPopupBaseCommand.TO_CLOSE:
			try:
				print('reopen')
				rowcol = self.current_rowcol()
				self.to_rowcol(self.rowcol)
				styled_popup.show_popup(self.view, self.html, on_hide=self.on_hide, on_navigate=self.on_navigate)
				self.to_rowcol(rowcol)
			except Exception as e:
				#will get exception when popup moves out of view, just close the pop up
				#not sure how to check that because self.view.sel() always return same object
				print(e)
				QOutPopupBaseCommand.TO_CLOSE = False
				QOutPopupBaseCommand.ACTUALLY_CLOSED = True
				self.view.hide_popup()
		else:
			QOutPopupBaseCommand.ACTUALLY_CLOSED = True

	def on_navigate(self, action):
		print(action)
		QOutPopupBaseCommand.TO_CLOSE = False
		print(self.view.id())
		self.view.hide_popup()

class QOutPopupCommand(QOutPopupBaseCommand):
	def do(self, edit=None, input=None):
		input = input.replace('\n', '<br>')
		input = input.replace(' ', '&nbsp;')
		return super().do(edit, input)

class QOutPopupJsonCommand(QOutPopupBaseCommand):
	def do(self, edit, input=None):
		input = sublime.decode_value(input)
		return super().do(edit, input)

class QOutPopupCloseCommand(QOutPopupBaseCommand):
    def do(self, edit=None, input=None):
        print('force close popup')
        QOutPopupBaseCommand.TO_CLOSE = False
        self.view.hide_popup()
       	return ''	#return something so q_chain can continue
