import sublime, sublime_plugin
from . import q_chain
import ast
from . import q_select_text
from . import q_send
from . import QCon

#show output in phantom
#see https://www.sublimetext.com/docs/3/api_reference.html#sublime.Phantom
#and example in https://forum.sublimetext.com/t/dev-build-3118/21270
class QOutPhantomCommand(q_chain.QChainCommand):

  def __init__(self, view):
    self.view = view
    active_phantom_ids = self.view.settings().get('active_phantom_ids')
    if not active_phantom_ids:
      self.view.settings().set('active_phantom_ids', [])

  def do(self, edit, input=None):
    location = self.view.sel()[0].end()
    id = str(location)
    html = self.render_text_result(input, id)
    self.add_phantom(html, id, location)

  def render_text_result(self, input, id):
    inputx = input.split("\n")
    c = len(inputx)
    if c > 10:
      inputx = inputx[0:10]
      inputx.append("...({0} more)".format(c-10-1)) #-2 for header rows
    inputx = "<br>".join(inputx)

    template = '<a href="close[{0}" style="display:inline;color:grey;">x</a> {1}'
    html = template.format(id, inputx)
    return html

  def add_phantom(self, html, id, location):
    #remove old one first if exist
    active_phantom_ids = self.view.settings().get('active_phantom_ids')
    if id in active_phantom_ids:
      self.view.erase_phantoms(id)
    else:
      active_phantom_ids.append(id)
      self.view.settings().set('active_phantom_ids', active_phantom_ids)

    self.view.add_phantom(id,
      sublime.Region(location),
      html,
      sublime.LAYOUT_BLOCK,
      self.on_navigate
    )

  def remove_phantom(self, id):
    active_phantom_ids = self.view.settings().get('active_phantom_ids')
    active_phantom_ids.remove(id)
    self.view.erase_phantoms(id)
    self.view.settings().set('active_phantom_ids', active_phantom_ids)

  def on_navigate(self, href):
    try:
      x = href.split('[')
      if x[0] == 'close':
        id = x[1]
        self.remove_phantom(id)
        return True
      #else:
        #print("unknown href: {0}".format(href))
    except Exception as e:
      #print(active_phantom_ids)
      #print(href)
      sublime.error_message("Phatom navigation error\nactive_phantom_ids: {0}\nhref: {1}\nerror: {2}".format(active_phantom_ids, href, e))
    return False

class QBrowseTablePhantomCommand(QOutPhantomCommand):

  def run(self, edit):
    self.get_table(None, 0, self.view.sel()[0].end())

  def get_table(self, table, index, location):
    con = QCon.QCon.loadFromViewWithPrompt(self.view)
    if con:
      if not table:
        table = q_select_text.QSelectWordCommand.selectWord(self.view)
      statement = ".h.jx[{1}] `{0}".format(table, index)
      res = q_send.QSendRawCommand.sendAndUpdateStatus(self.view, con, statement)
      #print(res)

      id = str(location)
      html = self.render_html_result(res, id, table)
      self.add_phantom(html, id, location)

  def render_html_result(self, input, id, table):
    inputx = [x.decode('utf-8') for x in ast.literal_eval(input)]
    inputx[0] = inputx[0].replace('href="?[', 'href="?[{0}[{1}['.format(id, table))
    inputx = "<br>".join(inputx)

    template = '<a href="close[{0}" style="display:inline;color:grey;">x</a> {1}'
    html = template.format(id, inputx)
    return html

  def on_navigate(self, href):
    if not super().on_navigate(href):
      try:
        x = href.split('[')
        if x[0] == '?':
          id = x[1]
          table = x[2]
          index = x[3]
          self.get_table(table, index, int(id))
          return True
        else:
          print("unknown href: {0}".format(href))
      except Exception as e:
        sublime.error_message("Phatom navigation error\nactive_phantom_ids: {0}\nhref: {1}\nerror: {2}".format(active_phantom_ids, href, e))
    return False

class QCloseLastPhantomCommand(q_chain.QChainCommand):

  def do(self, edit, input=None):
    #only remove phantom if no output panel
    output_showing = self.view.window().active_panel() == "output.q"
    if not output_showing:
      active_phantom_ids = self.view.settings().get('active_phantom_ids')
      if active_phantom_ids:
        last_phantom = active_phantom_ids.pop()
        self.view.erase_phantoms(last_phantom)
        self.view.settings().set('active_phantom_ids', active_phantom_ids)
    return '' #return something so q_chain may continue

#show output in phantom
#LAYOUT_INLINE, LAYOUT_BLOCK, LAYOUT_BELOW
#see example here https://forum.sublimetext.com/t/dev-build-3118/21270
#Save it as a new plugin, then start editing a plain text file with content along the lines of ```how many characters is this =>`
"""class ViewCalculator(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        self.view = view
        self.phantom_set = sublime.PhantomSet(view)
        self.timeout_scheduled = False
        self.needs_update = False

        self.update_phantoms()

    @classmethod
    def is_applicable(cls, settings):
        syntax = settings.get('syntax')
        return syntax == 'Packages/Text/Plain text.tmLanguage'

    def update_phantoms(self):
        phantoms = []

        # Don't do any calculations on 1MB or larger files
        if self.view.size() < 2**20:
            candidates = self.view.find_all('=>')

            for r in candidates:
                line_region = self.view.line(r.a)

                line = self.view.substr(line_region)

                idx = r.a - line_region.a
                if idx != -1:
                    val = len(line[0:idx].strip())

                    op_pt = line_region.a + idx

                    phantoms.append(sublime.Phantom(
                        sublime.Region(op_pt + 2),
                        str(val),
                        sublime.LAYOUT_BLOCK))

        self.phantom_set.update(phantoms)

    def handle_timeout(self):
        self.timeout_scheduled = False
        if self.needs_update:
            self.needs_update = False
            self.update_phantoms()

    def on_modified(self):
        # Call update_phantoms(), but not any more than 10 times a second
        if self.timeout_scheduled:
            self.needs_update = True
        else:
            sublime.set_timeout(lambda: self.handle_timeout(), 100)
            self.update_phantoms()
"""