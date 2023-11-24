from . import q_chain

#show_q_output
class QOutPanelCommand(q_chain.QChainCommand):

	def do(self, edit, input=None):
		input = input.replace('\r', '')
		panel = self.view.window().get_output_panel("q")
		syntax_file = "Packages/q KDB/syntax/q_output.tmLanguage"
		try:
			panel.set_syntax_file(syntax_file)
		except Exception:
			print("Unable to load syntax file: ", syntax_file)

		panel.settings().set("word_wrap", False)

		panel.set_read_only(False)
		# panel.insert(edit, panel.size(), input)
		panel.run_command("append", {"characters": input})
		panel.set_read_only(True)
		self.view.window().run_command("show_panel", {"panel": "output.q"})
		return '' #return something so that the chain will continue

class QHideOutPanelCommand(q_chain.QChainCommand):

	def do(self, edit, input=None):
		self.view.window().run_command("hide_panel", {"panel": "output.q"})
		return ''	#return something so q_chain can continue
