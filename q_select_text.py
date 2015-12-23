from . import chain

class QSelectTextCommand(chain.ChainCommand):       
    def do(self, edit, input=None):
        # get s
        s = self.selectText()

        # only proceed if s is not empty
        if(s == "" or s == "\n"):
            return
        else:
            return s

    def selectText(self):
        s = ""
        for region in self.view.sel():
            if region.empty():
                s += self.view.substr(self.view.line(region))
                #if advanceCursor:
                #    self.advanceCursor(region)
            else:
                s += self.view.substr(region)
        return s

    #not used
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



  
