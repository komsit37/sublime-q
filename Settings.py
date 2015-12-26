import sublime, sublime_plugin
from . import QCon as Q

class Settings():
	package = {}

	@staticmethod
	def save():
		sublime.save_settings('sublime-q.sublime-settings')

	@staticmethod
	def add_connection(qcon):
		con_dicts = Settings.get('connections')
		if not Settings.has_connection(qcon):
			con_dicts.insert(0, qcon.toDict())	#then add to top
			Settings.set('connections', con_dicts)
			Settings.save()

	@staticmethod
	def delete_connection(qcon):
		con_dicts = Settings.get('connections')
		con_dicts = list(filter(lambda x: not qcon.equals(x), con_dicts))
		Settings.set('connections', con_dicts)
		Settings.save()

	@staticmethod
	def move_to_top(qcon):
		Settings.delete_connection(qcon)
		Settings.add_connection(qcon)

	@staticmethod
	def update_connection(qcon, new_qcon):
		con_dicts = Settings.get('connections')
		for i, c in enumerate(con_dicts):	#modoify existing qcon
			if qcon.equals(c):
				con_dicts[i] = new_qcon.toDict()

		Settings.package.set('connections', con_dicts)
		Settings.save()

	@staticmethod
	def has_connection(qcon):
		con_dicts = Settings.get('connections')
		for c in con_dicts:	#modoify existing qcon
			if qcon.equals(c):
				return True
		return False

	@staticmethod
	def get(key):
		if not Settings.package:
			Settings.package = sublime.load_settings('sublime-q.sublime-settings')

		return Settings.package.get(key)

	@staticmethod
	def set(key, value):
		Settings.package.set(key, value)

	#actual use
	@staticmethod
	def default_new_connection():
		return Settings.get('default_new_connection')

	@staticmethod
	def get_connections():
		return Settings.get('connections') or []