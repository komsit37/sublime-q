from . import chain

#show_q_output
class QOutPanelCommand(chain.ChainCommand):

	def do(self, edit, input=None):
		panel = self.view.window().get_output_panel("q")
		panel.set_syntax_file("Packages/sublime-q/syntax/q_output.tmLanguage")
		panel.settings().set("word_wrap", False)

		panel.set_read_only(False)
		panel.insert(edit, panel.size(), input)
		panel.set_read_only(True)
		self.view.window().run_command("show_panel", {"panel": "output.q"})
		return '' #return something so that the chain will continue