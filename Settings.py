import sublime, sublime_plugin
from . import QCon as Q

class Settings():
	package = {}

	def save(self):
		sublime.save_settings('sublime-q.sublime-settings')

	def add_connection(self, qcon):
		con_dicts = self.get('connections')
		if not self.has_connection(qcon):
			con_dicts.insert(0, qcon.toDict())	#then add to top
			self.set('connections', con_dicts)
			self.save()

	def delete_connection(self, qcon):
		con_dicts = self.get('connections')
		con_dicts = list(filter(lambda x: not qcon.equals(x), con_dicts))
		self.set('connections', con_dicts)
		self.save()

	def move_to_top(self, qcon):
		self.delete_connection(qcon)
		self.add_connection(qcon)

	def update_connection(self, qcon, new_qcon):
		con_dicts = self.get('connections')
		for i, c in enumerate(con_dicts):	#modify existing qcon
			if qcon.equals(c):
				con_dicts[i] = new_qcon.toDict()

		self.package.set('connections', con_dicts)
		self.save()

	def has_connection(self, qcon):
		con_dicts = self.get('connections')
		for c in con_dicts:	#modify existing qcon
			if qcon.equals(c):
				return True
		return False

	def get(self, key):
		if not self.package:
			self.package = sublime.load_settings('sublime-q.sublime-settings')

		return self.package.get(key)

	def set(self, key, value):
		self.package.set(key, value)

	#actual use
	def default_new_connection(self):
		return self.get('default_new_connection')

	def get_connections(self):
		return self.get('connections') or []