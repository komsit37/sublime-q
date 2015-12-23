import sublime
import sublime_plugin

class CmdChainCommand(sublime_plugin.TextCommand):
        
    def run(self, edit, chain=None):
        if chain is not None:
            if len(chain) > 0:
                self.view.run_command(chain[0], {"text": res, "chain": chain[1:]})
        else:
            #no chain - just print output to console
            print(res)



  
