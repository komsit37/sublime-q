# q REPL for Sublime Text 3
Connect to remote q session and execute q statements in Sublime Text

![Image of screenshot](https://github.com/komsit37/sublime-q/blob/master/resources/showcase.gif)
* `Cmd + alt + q` to add q connections and quickly switch between them
* `Cmd + Enter` or `Cmd + e` to send highlighted line or block text  
* `Cmd + j` to execute text and get result as json (by calling .j.j to results - requires .j.j in kdb 3.x)
* 2 result modes: **output panel** and **inline popup**
* Syntax higlighing (based on kimtang's https://github.com/kimtang/sublime-q)  
* shows rows, column, time, mem usage at status bar  
* auto complete  
[change Cmd to Ctrl for windows]

### Shortcut 

* `F1` open help at cursor</li>
* `F2` print variable at cursor</li>
* `F3` show type at cursor</li>
* `F4` show table and columns</li>
* `F5` show environments</li>
* `shift + F5` show memory usage</li>

[hold shift to show output in inline popup instead of output panel]


## Installation
via package control https://packagecontrol.io/packages/q%20KDB


## Contribute

Clone this git repository into your `Sublime Text 3/Packages` directory.
NOTE: You may need to change dir to `q KDB`

* Windows: `C:\Users\[username]\AppData\Roaming\Sublime Text 3\Packages`
* OS X: `~/Library/Application Support/Sublime Text 3/Packages`

```
git clone https://github.com/komsit37/sublime-q.git
```
From sublime text, run package control: satisfy dependencies (you may need to open package folder in sublime text first). This will install numpy as a dependency package to your packages folder

Tested on OSX and Windows 8, 10


### Supported OS
* osx_x64
* windows_x64
* linux_x64

###Not supported OS
Support can be easily extended by adding proper numpy 1.8 build with python 3.3 (see https://github.com/komsit37/sublime-q/issues/12). Please send PR if you can build any of these:
* osx_x32
* windows_x32
* linux_x32

This plugin is for Sublime Text 3. For Sublime Text 2, please use https://github.com/komsit37/sublime-q-2

## To build numpy
Included numpy version should work for osx and windows 64bit, but if you need to build numpy

1. download python 3.3
2. download http://sourceforge.net/projects/numpy/files/NumPy/1.8.1/
3. run `python3.3 setup.py install`
4. numpy will be installed to your default python lib
5. then follow steps here https://github.com/komsit37/sublime-q/issues/12
