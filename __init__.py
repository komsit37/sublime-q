import sublime
#to be able to import module from subfolder
#http://stackoverflow.com/questions/279237/import-a-module-from-a-relative-path
import os, sys, inspect
#import qpython, numpy based on os_arch. numpy and qpython needs to be built for each os/architecture combination

#qpython is in package root path/lib
package_root_path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"lib")))
if package_root_path not in sys.path:
	print('sublime-q: adding folder ' + package_root_path + ' to sys.path')
	sys.path.insert(0, package_root_path)