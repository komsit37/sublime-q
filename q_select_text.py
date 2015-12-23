import sublime
import sublime_plugin

class QSelectTextCommand(sublime_plugin.TextCommand):
        
    def run(self, edit, advanceCursor=False, chain=None):
        # get s
        s = self.selectText(advanceCursor)

        # only proceed if s is not empty
        if(s == "" or s == "\n"):
            return
        #s = s.encode('ascii')  # qpy needs ascii
        if chain is not None and len(chain) > 0:
            self.view.run_command(chain[0], {"text": s, "chain": chain[1:]})
        else:
            print(s)
        

    def selectText(self, advanceCursor):
        s = ""
        for region in self.view.sel():
            if region.empty():
                s += self.view.substr(self.view.line(region))
                if advanceCursor:
                    self.advanceCursor(region)
            else:
                s += self.view.substr(region)
        return s

    def advanceCursor(self, region):
        (row, col) = self.view.rowcol(region.begin())

        # Make sure not to go past end of next line
        nextline = self.view.line(self.view.text_point(row + 1, 0))
        if nextline.size() < col:
            loc = self.view.text_point(row + 1, nextline.size())
        else:
            loc = self.view.text_point(row + 1, col)

        # Remove the old region and add the new one
        self.view.sel().subtract(region)
        self.view.sel().add(sublime.Region(loc, loc))



  
