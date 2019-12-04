from . import q_chain

class QSelectTextCommand(q_chain.QChainCommand):
    def do(self, edit, input=None):
        # get s
        s = QSelectTextCommand.selectText(self.view)

        # only proceed if s is not empty
        if(s == "" or s == "\n"):
            return
        else:
            return s

    @staticmethod
    def selectText(view):
        s = ""
        for region in view.sel():
            if region.empty():
                s += view.substr(view.line(region))
                #if advanceCursor:
                #    advanceCursor(region)
            else:
                s += view.substr(region)
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

class QSelectWordCommand(q_chain.QChainCommand):
    def do(self, edit, input=None):
        # grab the word or the selection from the view
        region = self.view.sel()[0]
        location = False
        if region.empty():
            # if we have no selection grab the current word
            location = self.view.word(region)
        else:
            # grab the selection
            location = region

        if location and not location.empty():
            s = self.view.substr(location)
            scope = self.view.scope_name(location.begin()).rpartition('.')[2].strip()

        # only proceed if s is not empty
        if(s == "" or s == "\n"):
            return
        else:
            return s




