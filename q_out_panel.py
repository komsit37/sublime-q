import sublime, sublime_plugin

#show_q_output
class QOutPanelCommand(sublime_plugin.TextCommand):

	def run(self, edit, text, chain=None):
		print(text)
		#if not hasattr(self, 'panel'):
		panel = self.view.window().get_output_panel("q")
		panel.set_syntax_file("Packages/sublime-q/syntax/q_output.tmLanguage")
		panel.settings().set("word_wrap", False)

		panel.set_read_only(False)
		panel.insert(edit, panel.size(), text)
		panel.set_read_only(True)
		self.view.window().run_command("show_panel", {"panel": "output.q"})