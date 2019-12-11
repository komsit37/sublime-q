import sublime
import sublime_plugin
from . import QCon
from . import q_send
from . import q_select_text
import os
import webbrowser
#import pprint
from . import util

#copy code from https://github.com/nickjj/sublime-text-3-packages/blob/master/Packages/Gutter%20Color/gutter_color.py
def clear_and_reload_cache(force = False):
  """
  If the folder exists, and has more than 1MB of icons in the cache, delete and recreate
  copy template, js to cache
  """
  from os.path import getsize, isfile, exists
  from os import makedirs, listdir
  from shutil import rmtree

  #print(sublime.cache_path()) #/Users/pkomsit/Applications/Sublime Text.app/Contents/MacOS
  # The icon cache path
  # The maximum amount of space to take up
  limit = 1000000 # 1 MB

  if exists(cache_dir()):
    size = sum(getsize(cache_dir(f)) for f in listdir(cache_dir()) if isfile(cache_dir(f)))
    if force or (size > limit): rmtree(cache_dir())

  if not exists(cache_dir()): makedirs(cache_dir())

  #need to copy js file to cache so that our output html can find it
  settings = sublime.load_settings("sublime-q.sublime-settings")
  for resource in settings.get('scripts', []):
    copy_resource_to_cache(resource)

def cache_dir(f=None):
  if f is not None:
    return os.path.join(sublime.cache_path(), "sublime-q", f)
  else:
    return os.path.join(sublime.cache_path(), "sublime-q")

def copy_resource_to_cache(resource):
  file = resource.rsplit('/', 1)[1]
  dest = cache_dir(file)
  print("copying resource " + resource + " to " + dest)
  try:
    write_file(dest, sublime.load_resource(resource))
  except Exception as e:
    sublime.error_message("Unable to copy resource from '" + resource + "' to '" + dest + "\nerror: " + str(e))

#sublime life cycle - called when plugin load
def plugin_loaded():
  clear_and_reload_cache()

def write_file(out_file, data):
  f = open(out_file, "w")
  f.write(data)
  f.close()

def find_routine(name):
  settings = sublime.load_settings("sublime-q.sublime-settings")
  routine =  [x for x in settings.get('routines') if x['name'] == name]
  if len(routine) == 0:
    return None
  else:
    return routine[0]

class QRoutineCommand(sublime_plugin.TextCommand):

  def run(self, edit, name):
    con = QCon.QCon.loadFromView(self.view)
    if con:
      s = q_select_text.QSelectWordCommand.selectWord(self.view)
      routine =  find_routine(name)
      if routine:
        sublime.set_timeout_async(lambda: self.run_routine(routine, con, s), 0)
      else:
        sublime.message_dialog('Routine "' + name + '" not found. Please add it to sublime-q.sublime-settings')
    else:
      #connect first
      sublime.message_dialog('Sublime-q: Choose your q connection first!')
      self.view.window().run_command('q_show_connection_list')

  def run_routine(self, routine, con, input):
    #pprint.pprint(routine)
    command = routine['command']
    render = routine.get('render')

    q = con.q
    try:
      q.open()

      if routine.get('preload_qcode_file'):
        qcode = sublime.load_resource(routine['preload_qcode_file'])
        #print(qcode)
        q(qcode)

      if command.get('qfunction'):
        if input == "":
          input = "[]"
        #print(input)
        raw = q(command['qfunction'] + " " + input)
      else:
        raw = q(command['qstatement'])
      data = util.decode(raw)

      if command.get('output'):
        #print(data)
        self.view.run_command(command.get('output'), {"input": data})
        #todo: show the data in output view?

      if render:
        #print(template)
        #print(data)
        res = sublime.load_resource(render['template_file']).replace(render['template_string'], data)

        chart_file = cache_dir("sublime_q_out.html")
        print("rendered chart to " + chart_file)
        write_file(chart_file, res)

        url = "file://" + chart_file
        #new=1 open in new window
        #autoraise=False do not focus note: this setting doesn't work on my MAC
        #see https://docs.python.org/2/library/webbrowser.html
        webbrowser.open(url, new=1, autoraise=False)
        #webbrowser.open_new(url)
        #print(os.getcwd()) #/Users/pkomsit/Applications/Sublime Text.app/Contents/MacOS
    except Exception as e:
      sublime.error_message('Error in QRoutineCommand.run_routine:\n' + str(e))
      self.view.set_status('result', 'ERROR')
      self.view.set_status('q', con.status())
      raise e
    finally:
      q.close()



