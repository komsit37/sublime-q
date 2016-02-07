import sublime
import sublime_plugin

#chain command and parse output to next command inputs
#example
#view.run_command("chain", {"chain": ["q_select_text", "q_send", "q_out_panel"]})
#view.run_command("chain", {"input": "til 10", "chain": ["q_send", "q_out_panel"]})
#view.run_command("chain", {"input": "test output", "chain": ["q_out_panel"]})
class QChainCommand(sublime_plugin.TextCommand):
    def do(self, edit, input=None):
        if input is not None:
            return input
        else:
            return "start"  #to start chain

    def run(self, edit, input=None, chain=None):
        output = self.do(edit, input)
        if output is None:
            print('break chain because output is none')
            return

        if chain is not None:
            if len(chain) > 0:
                print('\tchain ' + str(len(chain)) + ' command ' + chain[0] + '...')
                self.view.run_command(chain[0], {"input": output, "chain": chain[1:]})
            else:
                print('finished chain')
        else:
            #no chain - just print output to console
            print(output)



  
