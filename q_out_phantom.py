import sublime, sublime_plugin
from . import q_select_text
from . import q_chain

#show output in phantom
#see https://www.sublimetext.com/docs/3/api_reference.html#sublime.Phantom
#and example in https://forum.sublimetext.com/t/dev-build-3118/21270
class QOutPhantomCommand(q_chain.QChainCommand):

  def __init__(self, view):
    self.view = view
    self.next_id = 0
    self.view.settings().set('phantoms', [])

  def get_next_id(self):
    id = self.next_id
    self.next_id = self.next_id + 1
    return id

  def do(self, edit, input=None):
    id = str(self.get_next_id())

    select_region = self.view.sel()[0]
    end_selection_region = sublime.Region(select_region.end(), select_region.end())

    template = '<a href="{0}" style="display:inline;color:grey;">x</a> {1}'
    html = template.format(id, input)

    self.view.add_phantom(id,
      end_selection_region,
      html,
      sublime.LAYOUT_BLOCK,
      self.on_navigate
    )
    phantoms = self.view.settings().get('phantoms')
    phantoms.append(id)
    self.view.settings().set('phantoms', phantoms)
    #self.phantom_set.update([])

  def on_navigate(self, id):
    phantoms = self.view.settings().get('phantoms')
    phantoms.remove(id)
    self.view.erase_phantoms(id)
    self.view.settings().set('phantoms', phantoms)

class QCloseLastPhantomCommand(q_chain.QChainCommand):

  def do(self, edit, input=None):
    #only remove phantom if no output panel
    panel = self.view.window().find_output_panel("q")
    output_showing = self.view.window().active_panel() == "output.q"
    if not output_showing:
      phantoms = self.view.settings().get('phantoms')
      if phantoms:
        last_phantom = phantoms.pop()
        self.view.erase_phantoms(last_phantom)
        self.view.settings().set('phantoms', phantoms)
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