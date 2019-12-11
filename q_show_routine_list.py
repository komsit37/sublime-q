import sublime, sublime_plugin

class QShowRoutineListCommand(sublime_plugin.WindowCommand):
  def run(self):
    #print('ShowRoutineListCommand')
    routines = sublime.load_settings("sublime-q.sublime-settings").get('routines')
    l = [['Add...', 'New Routine']]  #add new connection to first element in the list

    for r in routines:
      l.append([r['name'], r['description']])
    self.window.show_quick_panel(l, self.on_done, 0, 1)  #start at index 1 (so user can press up for new)

  def on_done(self, i):
    if i < 0:       #we get index=-1 if cancel
      return
    if i == 0:
      self.window.open_file(sublime.packages_path() + "/sublime-q/settings/sublime-q.sublime-settings")
      #self.window.open_file(sublime.packages_path() + "/User/sublime-q.sublime-settings")
    else:
      routines = sublime.load_settings("sublime-q.sublime-settings").get('routines')
      r = routines[i - 1] #since we added extra items when show
      #print(r['name'])
      self.window.run_command('q_routine', {'name': r['name']})