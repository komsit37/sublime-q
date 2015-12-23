import sublime
#to be able to import module from subfolder
#http://stackoverflow.com/questions/279237/import-a-module-from-a-relative-path
import os, sys, inspect
#import qpython, numpy based on os_arch. numpy and qpython needs to be built for each os/architecture combination

def add_to_syspath(path):
	print('adding folder ' + path + ' to sys.path')
	if path not in sys.path:
		sys.path.insert(0, path)

#qpython is in package root path/lib
package_root_path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"lib")))
add_to_syspath(package_root_path)

#numpy is in platform specific path (i.e. osx_x64)
platform_arch = sublime.platform() + '_' + sublime.arch()
arch_specific_path = package_root_path + '/' + platform_arch
if os.path.exists(arch_specific_path):
	add_to_syspath(arch_specific_path)
else:
	sublime.error_message('Sublime-q ERROR: Unsupported platform "' + platform_arch + '"\nTo enable support: build numpy 1.8 (for ' + platform_arch + ') and add it to ' + arch_specific_path)
	