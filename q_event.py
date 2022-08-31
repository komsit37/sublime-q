import sublime, sublime_plugin
from . import QCon as Q
from . import q_send
from . import Settings as S
from . import util

class QEvent(sublime_plugin.EventListener):
  settings = S.Settings()

  #update connection status when view is activated
  def on_activated_async(self, view):
    if (view.score_selector(0, 'source.q') != 0):       #only activated for q
      qcon = Q.QCon.loadFromView(view)
      if qcon:
        view.set_status('q', qcon.status())

  def on_query_completions(self, view, prefix, locations):
    if not view.match_selector(locations[0], "source.q") or not self.settings.get('use_completion'):
      return []
    compl = view.settings().get('q_compl')
    #print(compl)
    # sublime uses '.'to seperate words so dot will be replaced in autocomplete
    # we can work around this by guessing what the user wants, if the '.' is missing suggest dot completions
    cw = view.substr(sublime.Region(
        view.find_by_class(locations[0], False, 1, " "),locations[0]))
    nscompl = view.settings().get(
        'q_nscompl') if cw[0] == "." else view.settings().get('q_nscomplwdot')
    return compl+nscompl or []

#put this class in this file because it updates view settings 'q_compl'
class QUpdateCompletionsCommand(q_send.QSendRawCommand):
  settings = S.Settings()

  def query():
    t = '(tables `.)!cols each tables `.'
    v = '(system "v") except system"a"'
    f = 'system "f"'
    q = '1 _ key `.q'
    ns = "raze {(enlist x)!enlist 1 _ key x} each `$\".\",' string except[;`q] key `"
    return '`t`v`f`q`ns!({0}; {1}; {2}; {3}; {4})'.format(t, v, f, q, ns)

  def send(self, con, s):
    if not self.settings.get('use_completion'):
      return
    try:
      q = con.q
      q.open()
      res = q(QUpdateCompletionsCommand.query())
      #print(res)
      compl = []

      tb = res[b't']
      for x in tb.iteritems():
        t = x[0].decode('utf-8')
        compl.append((t + '\tTable', t))
        for c in x[1]:
          c = c.decode('utf-8')
          #print(c)
          compl.append((t + '\t' + c, c))
          compl.append((c + '\t' + t, c))

      compl.extend(self.makeCompletions(res[b'v'], 'Variable'))
      compl.extend(self.makeCompletions(res[b'f'], 'Function'))
      compl.extend(self.makeCompletions(res[b'q'], 'q'))
      compl.extend(self.makeCompletions(['select', 'from', 'update', 'delete'], 'q'))
      nscompl=[]
      nscomplwdot=[]
      ns = res[b'ns']
      for x in ns.iteritems():
        n = x[0].decode('utf-8')
        nscompl.append((n[1:] + '\tNamespace', n[1:]))
        nscomplwdot.append((n + '\tNamespace', n))
        for c in x[1]:
          c = c.decode('utf-8')
          #print(c)
          f = n + '.' + c
          nscompl.append((f[1:] + '\t' + n, f[1:]))
          nscomplwdot.append((f + '\t' + n, f))
      self.view.settings().set('q_compl', compl)
      self.view.settings().set('q_nscompl', nscompl)
      self.view.settings().set('q_nscomplwdot', nscomplwdot)
    finally:
      q.close()

  def makeCompletions(self, l, t):
    out = []
    for x in l:
      #v = x.decode('utf-8')
      v = util.decode(x)
      out.append((v + '\t' + t, v))
    return out

