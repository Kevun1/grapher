import sys
from cx_Freeze import setup, Executable

exe = Executable(
	script = r'grapher3d.py',
	base='Win32GUI'
	)

setup(
	name = "Calculus Grapher",
	version = 0.1,
	description = "3D Grapher",
	executables = [exe],
	includes = ['numpy', 'vtk', 'urllib', 'scipy', 'tvtk', 'mayavi', 'pyface', 'logging', 'traits', 
	'distutils', 'uuid', 'setuptools', 'apptools', 'traitsui', 'traitsui.qt4.toolkit', 'getpass', 'tty', 'http.server', 
	'netrc', 'pathlib', 'posixpath', 'shutil', 'tarfile', 'webbrowser'],
	)