import sublime
import sublime_plugin
from . import QCon
from . import q_send
from . import q_select_text
import os
import webbrowser
#import pprint
from . import util
from .qpython.qtype import QException
from socket import error as socket_error

#fix unicode encoding issue when rendering template with non-ascii string
#see https://stackoverflow.com/questions/9942594/unicodeencodeerror-ascii-codec-cant-encode-character-u-xa0-in-position-20
import os;
import locale;

os.environ["PYTHONIOENCODING"] = "utf-8";
myLocale=locale.setlocale(category=locale.LC_ALL, locale="");

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

  """
  name: name of routine to lookup from settings/sublime-q.sublime-settings
  x: additional parameter to pass to q statement
  example routine setting
    {
      "name": "list tables (phantom)",
      "description": "list tables in q sessions. show output in phantom",
      "command": {"qstatement": ".h.jx[{1}] `{0}", "output": "q_out_phantom"}
    }

  qstatement: is a template string with optional args where {0} is input from selected text in editor, {1} is optional args
  output: optional output command
  render: template file to render output results and display in browser
  """
  def run(self, edit, name, x=None):
    con = QCon.QCon.loadFromViewWithPrompt(self.view)
    if con:
      s = q_select_text.QSelectWordCommand.selectWord(self.view)
      routine =  find_routine(name)
      if routine:
        sublime.set_timeout_async(lambda: self.run_routine(routine, con, s, x), 0)
      else:
        sublime.message_dialog('Routine "' + name + '" not found. Please add it to sublime-q.sublime-settings')

  def run_routine(self, routine, con, input, x):
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

      statement = command['qstatement'].format(input, x)
      #print(statement)
      raw = q(statement)
      data = util.decode(raw)

      if command.get('output'):
        #print(data)
        self.view.run_command(command.get('output'), {"input": data})
        #todo: show the data in output view?

      if render:
        #print(template)
        #print(data)
        template = sublime.load_resource(render['template_file'])
        #print(template)
        #render data into placeholder {0} in template_file
        #can't ue str.format because it has issue with { in js code so you need to escape it like {{ but that makes the js code invalid
        res = template.replace('{0}', data)
        #print(res)

        chart_file = cache_dir("sublime_q_out.html")
        print("rendered chart to " + chart_file)
        write_file(chart_file, res)

        self.open_browser("file://" + chart_file)

    #todo: these two error handlings are duplicated from QSendRaw.executeRaw. try to refactor them
    except QException as e:
        error = "error: `" + util.decode(e)
        self.view.run_command(command.get('output'), {"input": error})
    except socket_error as serr:
        msg = 'Sublime-q cannot to connect to \n"' + con.h() + '"\n\nError message: ' + str(serr)
        sublime.error_message(msg)
        res = ""
        status = "error: " + str(serr)
    except Exception as e:
      sublime.error_message('Error in QRoutineCommand.run_routine:\n' + str(e))
      self.view.set_status('result', 'ERROR')
      self.view.set_status('q', con.status())
      raise e
    finally:
      q.close()

  def open_browser(self, url):
    #see https://docs.python.org/2/library/webbrowser.html
    browser_settings = sublime.load_settings("sublime-q.sublime-settings").get("browser")
    browser_type = browser_settings.get("browser_type", None)
    if browser_type == "default": #we need to put in None to use system default browser
      browser_type = None
    browser_new = browser_settings.get("new", 2) #new=2 open in new tab
    browser_autoraise = browser_settings["autoraise"] == "True" #autoraise=False do not focus note: this setting doesn't work on my mac
    webbrowser.get(browser_type).open(url, new=browser_new, autoraise=browser_autoraise)



