import sublime, sublime_plugin

class Settings():
	package = sublime.load_settings('sublime-q.sublime-settings')

	@staticmethod
	def save():
		sublime.save_settings('sublime-q.sublime-settings')

	@staticmethod
	def default_new_connection():
		return Settings.package.get('default_new_connection')

	@staticmethod
	def add_connection(name, h):
		connections = Settings.package.get('connections')
		connections = list(filter(lambda x: x['h'] != h, connections))
		connections.append({"name": name, "h": h})
		Settings.package.set('connections', connections)
		Settings.save()

	@staticmethod
	def delete_connection(h):
		connections = Settings.package.get('connections')
		connections = list(filter(lambda x: x['h'] != h, connections))
		Settings.package.set('connections', connections)
		Settings.save()

	@staticmethod
	def update_connection(name, h, newh):
		connections = Settings.package.get('connections')
		connections = list(filter(lambda x: x['h'] != h, connections))
		connections.append({"name": name, "h": newh})
		print(connections)
		Settings.package.set('connections', connections)
		Settings.save()

	@staticmethod
	def get_connections():
		return Settings.package.get('connections')