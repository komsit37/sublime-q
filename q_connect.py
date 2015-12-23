import sublime, sublime_plugin
from . import QCon as Q
from . import Settings as S

class QPromptConnectionCommand(sublime_plugin.WindowCommand):
    def run(self, label, initial_value, next=None):
        self.next = next
        self.window.show_input_panel(label, initial_value, self.on_done, None, None)

    def on_done(self, handle):
        con = Q.QCon.fromH(handle)
        view = self.window.active_view()
        view.set_status('q', con.status())
        con.saveToView(view)
        if self.next:
            self.next(con)

class QPromptNewConnectionCommand(sublime_plugin.WindowCommand):
    def run(self, next=None):
        prompt = QPromptConnectionCommand(self.window)
        prompt.run('New q Connection', S.Settings.default_new_connection(), next)
        
class QPromptEditConnectionCommand(sublime_plugin.WindowCommand):
    def run(self, next=None):
        con = Q.QCon.loadFromView(self.window.active_view())
        prompt = QPromptConnectionCommand(self.window)
        prompt.run('Edit q Connection', con.h(), next)



class QTestConnectionCommand(sublime_plugin.WindowCommand):
    def run(self):
        con = Q.QCon.loadFromView(self.window.active_view())
        if con:
            self.set_status(con)
        else:   #prompt for connection if not available
            prompt = QPromptNewConnectionCommand(self.window)
            prompt.run(self.set_status)

    def set_status(self, con):
        self.window.active_view().set_status('q', con.status())



class QAddConnectionCommand(sublime_plugin.WindowCommand):
    def run(self):
        con = Q.QCon.loadFromView(self.window.active_view())
        if con:
            self.prompt_name(con)
        else:   #prompt for connection if not available
            prompt = QPromptNewConnectionCommand(self.window)
            prompt.run(self.prompt_name)

    def prompt_name(self, con):
        self.h = con.h()
        self.window.show_input_panel('Connection Name', self.h, self.on_done, None, None)

    def on_done(self, name):
        S.Settings.add_connection(name, self.h)
        self.window.active_view().set_status('qstatus', 'saved as ' + name)



class QShowConnectionListCommand(sublime_plugin.WindowCommand):
    def run(self, next=None):
        self.next = next
        self.prompt_connections()

    def prompt_connections(self):
        self.cons = S.Settings.get_connections()
        l = list(map(lambda x:[x['name'], x['h']], self.cons))
        self.window.show_quick_panel(l, self.on_done)

    def on_done(self, i):
        if i >= 0:
            obj = self.cons[i]
            self.name = obj['name']
            self.h = obj['h']
            con = Q.QCon.fromH(obj['h'])
            if self.next:
                self.next(con)

class QListConnectionCommand(QShowConnectionListCommand):
    def run(self, action):
        #prompt = QShowConnectionListCommand(self.window)
        if action == 'open':
            super().run(self.open)
        elif action == 'update':
            super().run(self.update)
        elif action == 'delete':
            super().run(self.delete)
        elif action == 'rename':
            super().run(self.rename)

    def open(self, con):
        view = self.window.active_view()
        view.set_status('q', con.status())
        con.saveToView(view)
        self.window.active_view().set_status('qstatus', 'opened ' + self.name)

    def update(self, con):
        self.con = con
        QPromptConnectionCommand(self.window).run('Update q Connection', con.h(), self.update2)

    def update2(self, con):
        S.Settings.update_connection(self.name, self.h, con.h())
        self.window.active_view().set_status('qstatus', 'updated ' + self.name)

    def rename(self, con):
        self.con = con
        self.window.show_input_panel('Rename Connection', self.name, self.rename2, None, None)

    def rename2(self, name):
        S.Settings.update_connection(name, self.h, self.h)
        self.window.active_view().set_status('qstatus', 'renamed ' + name)

    def delete(self, con):
        S.Settings.delete_connection(con.h())
        self.window.active_view().set_status('qstatus', 'deleted ' + self.name)






















