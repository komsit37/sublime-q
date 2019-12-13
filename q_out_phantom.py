import sublime, sublime_plugin
from . import q_chain
import ast
from . import q_select_text
from . import q_send
from . import QCon

def get_preview_limit():
  return int(sublime.load_settings("sublime-q.sublime-settings").get('phantom_preview_limit'))

"""
show output in phantom
see https://www.sublimetext.com/docs/3/api_reference.html#sublime.Phantom
and example in https://forum.sublimetext.com/t/dev-build-3118/21270
"""
class QOutPhantomCommand(q_chain.QChainCommand):
  close_template = '<a href="close[{0}" style="display:inline;color:grey;">x</a> {1}'
  def __init__(self, view):
    self.view = view
    self.phantoms = QPhantoms(view)

  def do(self, edit, input=None):
    location = self.view.sel()[0].end()
    phantom_data = self.render_text_result(input, location)
    self.phantoms.add_or_update(phantom_data, self.on_navigate)

  def render_text_result(self, multi_lines_str, location):
    preview_limit = get_preview_limit()

    id = str(location)
    lines = multi_lines_str.split("\n")
    full = QOutPhantomCommand.close_template.format(id, "<br>".join(lines))
    data = {'id': id, 'location': location, 'full': full, 'preview': '', 'layout': sublime.LAYOUT_BLOCK, 'display': 'full'}

    nlines = len(lines)
    if nlines > preview_limit:
      previews = lines[0:preview_limit]
      previews.append('<a href="expand[{0}" style="display:inline;color:grey;">...({1} more lines)</a>'.format(id, nlines-preview_limit))
      preview = QOutPhantomCommand.close_template.format(id, "<br>".join(previews))
      data['preview'] = preview
      data['display'] = 'preview'

    return data

  def on_navigate(self, href):
    try:
      x = href.split('[')
      if x[0] == 'close':
        id = x[1]
        self.phantoms.remove(id)
        return True
      elif x[0] == 'expand':
        id = x[1]
        data = self.phantoms.get_data(id)

        if data:
          data['display'] = 'full'
          self.phantoms.add_or_update(data, self.on_navigate)
        else:
          print('trying to expand non-existent phantom id: ' + id)
        return True
      else:
        return False
    except Exception as e:
      sublime.error_message("Phatom navigation error\nhref: {0}\nerror: {1}".format(href, e))
      raise e

"""
show browseable html table in phantom utilizing .h.jx. input is table name (without `)
"""
class QBrowseTablePhantomCommand(QOutPhantomCommand):

  def run(self, edit):
    self.get_table(None, 0, self.view.sel()[0].end())

  def get_table(self, table, index, location):
    preview_limit = get_preview_limit()
    con = QCon.QCon.loadFromViewWithPrompt(self.view)
    if con:
      if not table:
        table = q_select_text.QSelectWordCommand.selectWord(self.view)
      #we need to set \C to limit table rows, but I don't want to alter existing setting, so save it first and restore it
      statement = '{{C: system "C"; system "C {2} 2000"; res: @[.h.jx[{1}]; x; {{raze "error: `", string x}}]; system "C ", " " sv string C; res}} `{0}'.format(table, index, preview_limit)
      uneval_str = q_send.QSendRawCommand.sendAndUpdateStatus(self.view, con, statement)
      #print(uneval_str)
      data = self.render_html_result(uneval_str, location, table)
      self.phantoms.add_or_update(data, self.on_navigate)

  def render_html_result(self, uneval_str, location, table):
    id = str(location)
    try:
      lines = [x.decode('utf-8') for x in ast.literal_eval(uneval_str)]
    except SyntaxError as e:
      print('eval error: ' + str(e) + '. falling back to (uneval) str')
      lines = [uneval_str]
    #kdb function .h.jx i.e. creates line for next page "?[100", next row is 100
    #but we add our phantom id between so we can find the right phantom (in on_navigate) from href when clicked
    #so now the href looks like this "?[{id}[100"
    lines[0] = lines[0].replace('href="?[', 'href="?[{0}['.format(id))
    lines = "<br>".join(lines)

    html = QOutPhantomCommand.close_template.format(id, lines)
    return {'id': id, 'location': location, 'full': html, 'preview': '', 'layout': sublime.LAYOUT_BLOCK, 'display': 'full', 'table': table}

  def on_navigate(self, href):
    if not super().on_navigate(href):
      try:
        x = href.split('[')
        if x[0] == '?':
          id = x[1]
          index = x[2]
          data = self.phantoms.get_data(id)
          if data:
            self.get_table(data['table'], index, data['location'])
          else:
            print('trying to get table name from non-existent phantom id: ' + id)
          return True
        else:
          print("unknown href: {0}".format(href))
          return False
      except Exception as e:
        print("Phatom navigation error\nhref: {0}\nerror: {1}".format(href, e))
        raise e


class QCloseLastPhantomCommand(QOutPhantomCommand):
  def do(self, edit, input=None):
    #only remove phantom if no output panel
    output_showing = self.view.window().active_panel() == "output.q"
    if not output_showing:
      self.phantoms.remove_last()
    return '' #return something so q_chain may continue

"""
wrap phantom related settings and code
"""
class QPhantoms:
  def __init__(self, view):
    self.view = view
    #a list to keep track of last phantom id pre view. This allos closing them in reverse order when pressing esc (QCloseLastPhantomCommand)
    active_phantom_ids = self.view.settings().get('active_phantom_ids')
    if not active_phantom_ids:
      self.view.settings().set('active_phantom_ids', [])
    #a dict to store phantom data per view
    phantom_data = self.view.settings().get('phantom_data')
    if not phantom_data:
      self.view.settings().set('phantom_data', {})

  def get_data(self, id):
    phantom_data = self.view.settings().get('phantom_data')
    return phantom_data.get(id, None)

  def add_or_update(self, data, on_navigate):
    phantom_data = self.view.settings().get('phantom_data')

    if data['id'] in phantom_data:
      self.view.erase_phantoms(data['id'])
    else:
      phantom_data[data['id']] = data
      self.view.settings().set('phantom_data', phantom_data)

    #add to active phantom ids so we can remove the last one by pressing esc
    active_phantom_ids = self.view.settings().get('active_phantom_ids')
    if not data['id'] in active_phantom_ids:
      active_phantom_ids.append(data['id'])
      self.view.settings().set('active_phantom_ids', active_phantom_ids)

    self.view.add_phantom(data['id'],
      sublime.Region(data['location']),
      data[data['display']], #selectively show preview or full data
      data['layout'],
      on_navigate
    )

  def remove(self, id):
    phantom_data = self.view.settings().get('phantom_data')
    if id in phantom_data:
      del phantom_data[id]
    else:
      print('trying to remove non-existent phantom id: ' + id + '\n phantom_data: ' + phantom_data)
    self.view.settings().set('phantom_data', phantom_data)

    active_phantom_ids = self.view.settings().get('active_phantom_ids')
    active_phantom_ids.remove(id)
    self.view.settings().set('active_phantom_ids', active_phantom_ids)

    self.view.erase_phantoms(id)

  def remove_last(self):
    active_phantom_ids = self.view.settings().get('active_phantom_ids')
    if active_phantom_ids:
      last_phantom_id = active_phantom_ids.pop()
      self.remove(last_phantom_id)


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