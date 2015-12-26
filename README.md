# q REPL for Sublime Text 3

* Cmd + Enter or Cmd + e to send highlighted text or block text  
* 2 result modes: output panel and inline popup
* Cmd + q to quickly switch between connections (configured in Preferences->Package Settings->sublime-q)  
* Syntax higlighing (based on kimtang's https://github.com/kimtang/sublime-q)  
* shows rows, column, time at status bar  
* auto complete

<ul>shortcut (hold shift to show output in inline popup)
<li>f1 open help at cursor</li>
<li>f2 print variable at cursor</li>
<li>f3 show type at cursor</li>
<li>f4 show table and columns</li>
<li>f5 show environments</li>
<li>shift + f5 show memory usage</li>
</ul>


Requires custom numpy 1.8 build for each platform/architecture. Support can be easily extended by adding proper numpy build to lib/[os]_[architecture]
###Supported
* osx_x64

###Not supported
* osx_x32
* windows_x64
* windows_x32
* linux_x32
* linux_x64

## Installation

Clone this git repository into your `Sublime Text 3/Packages` directory. 

* Windows: `%APPDATA%\Sublime Text 3\Packages`
* OS X: `~/Library/Application Support/Sublime Text 3/Packages`
* Linux: `~/.config/sublime-text-3`

```
git clone https://github.com/komsit37/sublime-q-3.git
```
Only tested on OSX

## To build numpy
Included numpy version should work for osx 64bit, but if you need to build numpy

1. download python 3.3
2. download http://sourceforge.net/projects/numpy/files/NumPy/1.8.1/
3. run
```
python3.3 setup.py install
```
4. numpy will be installed to your default python lib. copy and paste the whole folder to ib/[os]_[architecture]


to check your numpy version and installed directory, open console from sublime text cmd + ` (sublimetext may use different versions from your osx terminal)
>>> import numpy<br>
>>> numpy.__version__<br>
'1.6.2'<br>
>>> numpy.__file__<br>
'/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/numpy/__init__.pyc'<br>

to remove numpy 1.6.2<br>
open terminal<br>
cd /System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/<br>
sudo mv numpy numpy_old<br>

Update: Since OSX El Captain, you can't remove default python package with root. You will need to reboot into recovery mode (Command-R at startup logo), and run `csrutil disable` in terminal. see below link for more details 
https://apple.stackexchange.com/questions/193368/what-is-the-rootless-feature-in-el-capitan-really
