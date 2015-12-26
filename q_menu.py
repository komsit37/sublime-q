import sublime, sublime_plugin
from . import QCon as Q
from . import Settings as S

class PerViewCommand(sublime_plugin.WindowCommand):
    def view(self):
        return self.window.active_view()

    def local(self):
        return self.view().settings()

    def g(self):
        return S.Settings

    def getCurrentConnection(self):
        qcon_dict = self.local().get('q_handle')
        if qcon_dict:
            return Q.QCon.fromDict(qcon_dict)
        return None

    def isCurrentConnection(self, qcon):
        current = self.getCurrentConnection()
        return current and current.equals(qcon)

    def deleteConnection(self):
        return self.local().set('q_handle', None)

    def setConnection(self, qcon):
        self.local().set('q_handle', qcon.toDict())

    def set_status(self, tag, message, temp=False):
        self.view().set_status(tag, message)
        if temp:
            sublime.set_timeout(lambda:self.set_status(tag, ''), 3000)

    def loadQCons(self):
        con_dicts = S.Settings.get_connections()
        self.qcons = []
        for con_dict in con_dicts:
            self.qcons.append(Q.QCon.fromDict(con_dict))
        return self.qcons

class ShowConnectionListCommand(PerViewCommand):
    ACTIONS = ['Use', 'Use HDB', 'Update', 'Delete', 'Rename']

    def run(self):
        self.prompt_connection_list()

    def prompt_connection_list(self):
        qcons = self.loadQCons()

        l = [['Add...', 'New Connection']]  #add new connection to first element in the list
        #array of dict to array of array format as reqruired by show_quick_panel()
        current = self.getCurrentConnection()
        for qcon in qcons:
            c = ' [Current]' if qcon.equals(current) else ''
            item = [qcon.name + c, qcon.h()]
            l.append(item)
        self.window.show_quick_panel(l, self.prompt_actions, 0, 1)  #start at index 1 (so user can press up for new)

    def prompt_actions(self, i):
        if i < 0:       #we get index=-1 if cancel
            return        
        elif i == 0:    #new connection
            self.window.run_command('new_connection')
            return
        
        self.qcon = self.qcons[i - 1]
        self.window.show_quick_panel(ShowConnectionListCommand.ACTIONS, self.on_done)

    def on_done(self, i):
        if i < 0:       #we get index=-1 if cancel
            return
        action = ShowConnectionListCommand.ACTIONS[i]
        action = action.replace(' ', '_').lower()
        print(action + ' ' + str(self.qcon.h()))
        self.window.run_command(action + '_connection', {'name': self.qcon.name, 'h': self.qcon.h()})


class NewConnectionCommand(PerViewCommand):
    def run(self):
        self.prompt_new_connection()

    def prompt_new_connection(self):
        self.window.show_input_panel('New q Connectionœ', S.Settings.default_new_connection(), self.prompt_name, None, None)

    def prompt_name(self, h):
        self.h = h
        self.window.show_input_panel('Connection Name', h, self.on_done, None, self.on_cancel)

    def on_cancel(self):
        self.on_done('')

    def on_done(self, name):
        self.window.run_command('use_connection', {'name': name, 'h': self.h})


class CommandWithQCon(PerViewCommand):
    def run(self, name, h):
        selected_qcon = Q.QCon.new(name, h)
        current = self.getCurrentConnection()
        if current and current.equals(selected_qcon):
            self.current = True
            self.qcon = current
        else:
            self.current = False
            self.qcon = selected_qcon
        self.do()

    def done(self):
        if self.current:
            self.setConnection(self.qcon)
        self.set_status('q', self.getCurrentConnection().status())

class UseConnectionCommand(CommandWithQCon):
    def do(self):
        S.Settings.move_to_top(self.qcon) #this will put use connection on the top of connection list
        self.qcon.useHdb(False)
        self.setConnection(self.qcon)
        self.done()

class UseHdbConnectionCommand(CommandWithQCon):
    def do(self):
        S.Settings.move_to_top(self.qcon) #this will put use connection on the top of connection list
        self.qcon.useHdb(True)
        self.setConnection(self.qcon)
        self.done()

class DeleteConnectionCommand(CommandWithQCon):
    def do(self):
        S.Settings.delete_connection(self.qcon)
        self.set_status('result', 'Deleted "' + self.qcon.name + '"', True)
        

class RenameConnectionCommand(CommandWithQCon):
    def do(self):
        self.window.show_input_panel('Rename Connection', self.qcon.name, self.on_done, None, None)

    def on_done(self, new_name):
        new_qcon = self.qcon.clone()
        new_qcon.name = new_name
        S.Settings.update_connection(self.qcon, new_qcon)
        self.set_status('result', 'Renamed "' + new_qcon.h() + '" to "' + new_qcon.name  + '"', True)
        self.qcon = new_qcon
        self.done()

class UpdateConnectionCommand(CommandWithQCon):
    def do(self):
        self.window.show_input_panel('Update Connection', self.qcon.h(), self.on_done, None, None)

    def on_done(self, new_h):
        new_qcon = self.qcon.clone()
        new_qcon.h(new_h)
        S.Settings.update_connection(self.qcon, new_qcon)
        self.set_status('result', 'Updated "' + self.qcon.name + '" to "' + new_qcon.h()  + '"', True)
        self.qcon = new_qcon
        self.done()

