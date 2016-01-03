# q REPL for Sublime Text 3
Connect to remote q session and execute selected q statements in Sublime Text

![Image of screenshot](https://github.com/komsit37/sublime-q-3/blob/master/resources/showcase.gif)
* Cmd + Enter or Cmd + e to send highlighted text or block text  
* Cmd + j to execute text and get result as json (by calling .j.j to results - requires .j.j in kdb 3.0+)
* 2 result modes: *output panel* and *inline popup*
* Cmd + alt + q to quickly switch between connections 
* Syntax higlighing (based on kimtang's https://github.com/kimtang/sublime-q)  
* shows rows, column, time, mem usage at status bar  
* auto complete
(change Cmd to Ctrl for windows)

### shortcut (hold shift to show output in inline popup)
<ul>
<li>f1 open help at cursor</li>
<li>f2 print variable at cursor</li>
<li>f3 show type at cursor</li>
<li>f4 show table and columns</li>
<li>f5 show environments</li>
<li>shift + f5 show memory usage</li>
</ul>

###Supported
* osx_x64
* windows_x64

###Not supported
Support can be easily extended by adding proper numpy 1.8 build with python 3.3 to lib/[os]_[architecture]. Please send PR if you can build any of these
* osx_x32
* windows_x32
* linux_x32
* linux_x64

## Installation

Clone this git repository into your `Sublime Text 3/Packages` directory.  
NOTE: Dir name needs to be `sublime-q` (not `sublime-q-3`)

* Windows: `%APPDATA%\Sublime Text 3\Packages`
* OS X: `~/Library/Application Support/Sublime Text 3/Packages`
* Linux: `~/.config/sublime-text-3`

```
git clone https://github.com/komsit37/sublime-q-3.git sublime-q
```
Only tested on OSX

## To build numpy
Included numpy version should work for osx 64bit, but if you need to build numpy

1. download python 3.3
2. download http://sourceforge.net/projects/numpy/files/NumPy/1.8.1/
3. run `python3.3 setup.py install`
4. numpy will be installed to your default python lib. copy and paste the whole folder to [sublime-q package]/lib/[os]_[architecture]
