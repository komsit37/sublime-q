import sublime
import sublime_plugin
from . import QCon
from . import q_send
from . import q_select_text
import os
import webbrowser

#copy code from https://github.com/nickjj/sublime-text-3-packages/blob/master/Packages/Gutter%20Color/gutter_color.py
def clear_cache(force = False):
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

  #copy file from resource to cache
  copy_resource_to_cache("canvasjs_template.html")
  copy_resource_to_cache("canvasjs.min.js")
  copy_resource_to_cache("q.js")

def cache_dir(f=None):
  if f is not None:
    return os.path.join(sublime.cache_path(), "sublime-q", f)
  else:
    return os.path.join(sublime.cache_path(), "sublime-q")

def copy_resource_to_cache(resource_name):
  source = os.path.join("Packages", "sublime-q", "chart", resource_name)
  dest = cache_dir(resource_name)
  #print("copy resource " + source + " to " + dest)
  write_file(dest, sublime.load_resource(source))

#sublime life cycle - called when plugin load
def plugin_loaded():
  clear_cache()

def render(template_file, data):
  #print("q_chart")
  fr = open(cache_dir(template_file), "r")
  template = fr.read()
  fr.close()
  #print(template)
  #print(data)
  return template.replace("{{chart}}", data)

def write_file(out_file, data):
  f = open(out_file, "w")
  f.write(data)
  f.close()


class QChartCommand(sublime_plugin.TextCommand):
  prepData = ".j.j {c: cols x; cx: c[0]; cy: 1 _ c; cxy: cx ,/: cy;{`type`markerType`showInLegend`legendText`dataPoints!(`line; `none; 1b; (cols x)1; `x`y xcol x)} each {flip x!y[x]}[;x] each cxy} .st.tmp"

  def run(self, edit):
    con = QCon.QCon.loadFromView(self.view)
    if con:
      sublime.set_timeout_async(lambda: self.get_data_and_render(con), 0)
    else:
      #connect first
      sublime.message_dialog('Sublime-q: Choose your q connection first!')
      self.view.window().run_command('show_connection_list')

  def get_data_and_render(self, con):
    #todo: cache template
    #todo: no need to load chart code everytime
    qcode = sublime.load_resource(os.path.join("Packages", "sublime-q", "chart", "canvasjs.q"))
    #print(qcode)
    q = con.q
    try:
      q.open()
      q(qcode)
      #raw = q(QChartCommand.prepData)
      raw = q(".j.j .st.autoChart .st.tmp")
      data = q_send.QSendRawCommand.decode(raw)

      res = render("canvasjs_template.html", data)
      chart_file = cache_dir("sublime_q_chart.html")
      print(chart_file)
      write_file(chart_file, res)

      url = "file://" + chart_file
      #new=1 open in new window
      #autoraise=False do not focus note: this setting doesn't work on my MAC
      #see https://docs.python.org/2/library/webbrowser.html
      webbrowser.open(url, new=1, autoraise=False)
      #webbrowser.open_new(url)
      #print(os.getcwd()) #/Users/pkomsit/Applications/Sublime Text.app/Contents/MacOS
    finally:
      q.close()



