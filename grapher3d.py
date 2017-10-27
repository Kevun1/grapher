import os
import re
import random
import pickle

import vtk
vtk.vtkObject.GlobalWarningDisplayOff()
from traits.api import HasTraits, Range, Instance, \
                    on_trait_change
from traitsui.api import View, Item, HGroup
from tvtk.pyface.scene_editor import SceneEditor
from mayavi.tools.mlab_scene_model import \
                    MlabSceneModel
from mayavi.core.ui.mayavi_scene import MayaviScene

import numpy as np
import mayavi.mlab as mlab
from numpy import pi, sin, cos, tan, arcsin, arccos, arctan, exp, log, log10, log2, power, sqrt, linspace, sign, absolute, sinh, cosh, tanh, arcsinh, arccosh, arctanh, ceil,\
floor, maximum, minimum

from sympy import symbols, diff
from sympy.physics.vector import ReferenceFrame
from sympy.physics.vector import curl

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import *
from tkinter.colorchooser import *

from elementcreator import ElementCreator
from elementeditor import ElementEditor
from element import Element
from vectorequation import VectorEquation
from verifier import Verifier
from parabola import Parabola

root = tk.Tk()

class Grapher:
	def __init__(self, element):
		self.element = element
		self.type = element.type
		if self.element.properties['resolution']:
			self.resolution = self.element.properties['resolution']*1j
		else:
			self.resolution = 100j

		if self.element.properties['color']:
			self.color = self.element.properties['color']
		else:
			self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

		self.color = tuple(float(x / 255) for x in self.color)
		self.color = tuple(1.0 if x > 1.0 else x for x in self.color)

		if self.element.properties['opacity']:
			self.opacity = self.element.properties['opacity']
		else:
			self.opacity = 0.5

	def graph(self):
		if self.type == 'Implicit':
			self.graph_implicit()
		elif self.type == 'Explicit':
			self.graph_explicit()
		elif self.type == 'Parametric Surface':
			self.graph_parametric_surface()
		elif self.type == "Parametric Curve":
			self.graph_parametric_curve()
		elif self.type == 'Vector Field':
			self.graph_vfield()

	def graph_implicit(self):
		bounds = self.element.properties['bounds']
		self.xmin = eval(self.element.properties['bounds'][0])
		self.xmax = eval(self.element.properties['bounds'][1])
		self.ymin = eval(self.element.properties['bounds'][2])
		self.ymax = eval(self.element.properties['bounds'][3])
		self.zmin = eval(self.element.properties['bounds'][4])
		self.zmax = eval(self.element.properties['bounds'][5])
		x, y, z = np.mgrid[self.xmin:self.xmax:self.resolution, self.ymin:self.ymax:self.resolution, self.zmin:self.zmax:self.resolution]

		surface = self.element.equation.get()
		surface = self.format_string(surface)

		def f(x, y, z):
			return eval(surface)

		if not self.element.properties['gradient'] or self.element.properties['gradient'] == 'gradient and surface':
			mlab.contour3d(x, y, z, f, contours=[0], opacity=self.opacity, color=self.color)
		if self.element.properties['gradient'] == 'gradient only' or self.element.properties['gradient'] == 'gradient and surface':
			u, v, w = self._gradient_xyz(surface)
			u, v, w = self._normalize(u, v, w)
			x1, y1, z1 = np.mgrid[self.xmin:self.xmax:20j, self.ymin:self.ymax:20j, self.zmin:self.zmax:20j]
			def grad(x, y, z):
				return eval(u), eval(v), eval(w)
			mlab.quiver3d(x1, y1, z1, grad, mask_points=int(0.003*20**3), scale_factor=0.65, color=(1, 1, 1))

	def graph_explicit(self):
		bounds = self.element.properties['bounds']
		self.xmin = eval(self.element.properties['bounds'][0])
		self.xmax = eval(self.element.properties['bounds'][1])
		self.ymin = eval(self.element.properties['bounds'][2])
		self.ymax = eval(self.element.properties['bounds'][3])
		self.zmin = eval(self.element.properties['bounds'][4])
		self.zmax = eval(self.element.properties['bounds'][5])
		x, y = np.mgrid[self.xmin:self.xmax:self.resolution, self.ymin:self.ymax:self.resolution]

		surface = self.element.equation.get()
		surface = self.format_string(surface)

		def f(x, y):
			z = 0
			z = eval(surface)
			z[z > self.zmax] = np.nan
			z[z < self.zmin] = np.nan
			return z

		if self.element.properties['representation'] == None:
			rep = 'surface'
		else:
			rep = self.element.properties['representation']		

		if self.element.properties['gradient'] != 'gradient only' and self.element.properties['level curves'] != 'show one':
			mlab.surf(x, y, f, opacity=self.opacity, color=self.color, representation=rep)
		if self.element.properties['level curves'] == 'show both' or self.element.properties['level curves'] == 'show one':
			mlab.contour_surf(x, y, f, contours=10)
		"""
		if self.element.properties['gradient'] == 'gradient only' or self.element.properties['gradient'] == 'gradient and surface':
			u, v, w = self._gradient_xy(surface)
			u, v = self._normalize2(u, v)
			x1, y1, z1 = np.mgrid[self.xmin:self.xmax:20j, self.ymin:self.ymax:20j, self.zmin:self.zmax:20j]
			def grad(x, y, z):
				return eval(u), eval(v), eval(w)
			mlab.quiver3d(x1, y1, z1, grad, mask_points=int(0.0025*20**3), scale_factor=0.75, color=(1, 1, 1))
		"""

	def graph_parametric_surface(self):
		bounds = self.element.properties['bounds']
		self.umin = eval(self.element.properties['bounds'][0])
		self.umax = eval(self.element.properties['bounds'][1])
		self.vmin = eval(self.element.properties['bounds'][2])
		self.vmax = eval(self.element.properties['bounds'][3])
		u, v = np.mgrid[self.umin:self.umax:self.resolution, self.vmin:self.vmax:self.resolution]

		parametrization = self.element.equation.get()
		x = parametrization[0]
		x = self.format_string(x)

		y = parametrization[1]
		y = self.format_string(y)

		z = parametrization[2]
		z = self.format_string(z)

		if self.element.properties['representation'] == None:
			rep = 'surface'
		else:
			rep = self.element.properties['representation']

		mlab.mesh(eval(x), eval(y), eval(z), opacity=self.opacity, color=self.color, representation=rep)

	def graph_parametric_curve(self):
		bounds = self.element.properties['bounds']
		self.tmin = eval(self.element.properties['bounds'][0])
		self.tmax = eval(self.element.properties['bounds'][1])
 
		t = np.linspace(self.tmin, self.tmax, self.resolution.imag*2)

		parametrization = self.element.equation.get()
		x = parametrization[0]
		x = self.format_string(x)

		y = parametrization[1]
		y = self.format_string(y)

		z = parametrization[2]
		z = self.format_string(z)

		mlab.plot3d(eval(x), eval(y), eval(z), opacity=self.opacity, color=self.color)

	def graph_vfield(self):
		bounds = self.element.properties['bounds']
		self.xmin = eval(self.element.properties['bounds'][0])
		self.xmax = eval(self.element.properties['bounds'][1])
		self.ymin = eval(self.element.properties['bounds'][2])
		self.ymax = eval(self.element.properties['bounds'][3])
		self.zmin = eval(self.element.properties['bounds'][4])
		self.zmax = eval(self.element.properties['bounds'][5])

		self.resolution = 20j

		x, y, z = np.mgrid[self.xmin:self.xmax:self.resolution, self.ymin:self.ymax:self.resolution, self.zmin:self.zmax:self.resolution]

		field = self.element.equation.get()
		u = field[0]
		u = self.format_string(u)

		v = field[1]
		v = self.format_string(v)

		w = field[2]
		w = self.format_string(w)

		def f(x, y, z):
			return eval(u), eval(v), eval(w)

		if self.element.properties['vector operation'] == 'curl':
			u, v, w = self._curl(u, v, w)

		if self.element.properties['normalize'] == 'normalize':
			u, v, w = self._normalize(u, v, w)
		if self.element.properties['normalize'] == 'flatten':
			u, v, w = self._flatten(u, v, w)

		if not self.element.properties['color']:
			self.color = None

		if self.element.properties['colormap']:
			self.colormap = self.element.properties['colormap']
		else:
			self.colormap = 'blue-red'

		if self.element.properties['cut plane']:
			src = mlab.pipeline.vector_field(x, y, z, f)
			mlab.pipeline.vector_cut_plane(src, mask_points=int(self.element.properties['mask points']*(self.resolution.imag)**3), 
				scale_factor=self.element.properties['scale factor'], color=self.color, colormap=self.colormap)
		else:
			mlab.quiver3d(x, y, z, f, mask_points=int(self.element.properties['mask points']*(self.resolution.imag)**3), 
				scale_factor=self.element.properties['scale factor'], color=self.color, colormap=self.colormap)

	def _normalize(self, u, v, w):
		u = '{u} / sqrt({u}**2 + {v}**2 + {w}**2)'.format(u=u, v=v, w=w)
		v = '{v} / sqrt({u}**2 + {v}**2 + {w}**2)'.format(u=u, v=v, w=w)
		w = '{w} / sqrt({u}**2 + {v}**2 + {w}**2)'.format(u=u, v=v, w=w)
		return u, v, w

	def _normalize2(self, u, v):
		u = '{u} / sqrt({u}**2 + {v}**2)'.format(u=u, v=v)
		v = '{v} / sqrt({u}**2 + {v}**2)'.format(u=u, v=v)
		return u, v

	def _flatten(self, u, v, w):
		u = 'sign({u}) * log(absolute({u}) + 1)'.format(u=u)
		v = 'sign({v}) * log(absolute({v}) + 1)'.format(v=v)
		w = 'sign({w}) * log(absolute({w}) + 1)'.format(w=w)
		return u, v, w

	def translate_symbols(self, s):
		s = s.replace('R_x', 'x')
		s = s.replace('R_y', 'y')
		s = s.replace('R_z', 'z')

		s = s.replace('R.x', '1*R.x')
		s = s.replace('R.y', '1*R.y')
		s = s.replace('R.z', '1*R.z')

		m = re.search(r'(?:(.*?)\*R\.x [\+\-] )?(?:(.*?)\*R\.y [\+\-] )?(?:(.*?)\*R\.z)?', s)
		if not m.group(1):
			x = '0'
		else:
			x = m.group(1)

		if not m.group(2):
			y = '0'
		else:
			y = m.group(2)

		if not m.group(3):
			z = '0'
		else:
			z = m.group(3)

		x = self.format_string(x)
		y = self.format_string(y)
		z = self.format_string(z)

		return x, y, z

	def _curl(self, u, v, w):
		R = ReferenceFrame('R')

		u = u.replace('x', 'R[0]')
		u = u.replace('y', 'R[1]')
		u = u.replace('z', 'R[2]')

		v = v.replace('x', 'R[0]')
		v = v.replace('y', 'R[1]')
		v = v.replace('z', 'R[2]')

		w = w.replace('x', 'R[0]')
		w = w.replace('y', 'R[1]')
		w = w.replace('z', 'R[2]')

		F = eval(u + ' * R.x + ' + v + ' * R.y + ' + w + ' * R.z')

		G = curl(F, R)

		return self.translate_symbols(str(G))

	def _gradient_xyz(self, s):
		x, y, z = symbols('x y z', real=True)
		f = eval(s)
		dx = self.format_string(str(diff(f, x)))
		dy = self.format_string(str(diff(f, y)))
		dz = self.format_string(str(diff(f, z)))

		return dx, dy, dz

	def _gradient_xy(self, s):
		x, y = symbols('x y', real=True)
		f = eval(s)
		dx = self.format_string(str(diff(f, x)))
		dy = self.format_string(str(diff(f, y)))
		return dx, dy, '0*x'

	def format_string(self, s):
		s = s.replace(' ', '')
		try:
			float(eval(s))
		except:
			pass
		else:
			s += '+0*x'
		return "(" + s.replace("^", "**") + ")"	

class Application:
	def __init__(self, root):
		self.root = root
		self.root.option_add('*tearOff', tk.FALSE)
		self.root.wm_title("Grapher")
		self.frame = ttk.Frame(self.root, padding=[5, 5, 5, 5])
		self.frame.grid(row=0, column=0, sticky=('n', 's', 'e', 'w'))

		self.element_number = 1

		self.create_widgets()
		self.create_equation_entry()
		self.create_menu()

		self.populate_widgets()

		self.savefile = None

		self.elements = []

		self.verifier = Verifier()

	def create_widgets(self):
		self.graph_label = tk.Label(self.frame, text="Graph:")
		self.equation_label = tk.Label(self.frame, text="Element List")


		self.graph_button = tk.Button(self.frame, text="Graph", command=self.graph)
		self.cancel_button = tk.Button(self.frame, text="Cancel", command=self.root.destroy)
		self.add_element_button = tk.Button(self.frame, text="Add Element", command=self.add_element)

	def create_equation_entry(self):
		self.canvas = tk.Canvas(self.frame, highlightthickness=0)

		self.element_frame = tk.Frame(self.canvas)

		self.scroll = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=self.scroll.set)

		self.element_frame.bind("<Configure>", self.on_frame_configure)

		self.canvas.create_window((4, 4), window=self.element_frame, anchor='nw')

	def on_frame_configure(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox('all'))

	def populate_widgets(self):
		self.graph_label.grid(row=1, column=1, sticky='w')
		self.equation_label.grid(row=2, column=1, sticky='w')

		self.canvas.grid(row=3, column=1, rowspan=3, columnspan=3, sticky=('n','s','e','w'))

		self.scroll.grid(row=3, column=3, rowspan=3, sticky=('n','s','w'))

		self.graph_button.grid(row=7, column=3, padx=5, sticky=('e','w'))
		self.cancel_button.grid(row=7, column=4, padx=5, sticky=('e','w'))
		self.add_element_button.grid(row=7, column=1, sticky=('w'))

		root.rowconfigure(0, weight=1)
		root.columnconfigure(0, weight=1)
		self.frame.rowconfigure(3, weight=1)
		for i in range(1, 2):
			self.frame.columnconfigure(i, weight=1)

	def create_menu(self):
		self.menubar = tk.Menu(self.root)
		self.root['menu'] = self.menubar

		self.menu_file = tk.Menu(self.menubar)
		self.menubar.add_cascade(menu=self.menu_file, label='File')

		self.menu_file.add_command(label='Open', command=self.open)
		self.menu_file.add_command(label='Save', command=self.save_file)
		self.menu_file.add_command(label='Save As', command=self.save_as)

		self.menu_file.entryconfig('Save', state='disabled')

		self.menu_view = tk.Menu(self.menubar)
		self.menubar.add_cascade(menu=self.menu_view, label='View')

		self.parallel_projection = tk.BooleanVar()
		self.menu_view.add_checkbutton(label='Parallel Projection', onvalue=True, offvalue=False, variable=self.parallel_projection)

		self.color_legend = tk.BooleanVar()
		self.menu_view.add_checkbutton(label='Color Gradient Legend', onvalue=True, offvalue=False, variable=self.color_legend)

		self.fgcolor = tk.StringVar()
		self.fgcolor.set('(255,255,255)')
		self.menu_view.add_command(label='Foreground Color', command=self._select_fgcolor)

		self.bgcolor = tk.StringVar()
		self.bgcolor.set('(127,127,127)')
		self.menu_view.add_command(label='Background Color', command=self._select_bgcolor)

		self.menu_misc = tk.Menu(self.menubar)
		self.menubar.add_cascade(menu=self.menu_misc, label='Misc')

		self.menu_misc.add_command(label='Paraboloid Example', command=self.parabola)

		self.menubar.add_command(label='About', command=self.about)

	def about(self):
		t = tk.Toplevel()
		x = self.root.winfo_x()
		y = self.root.winfo_y()
		t.geometry('+{0}+{1}'.format(x + 35, y + 35))
		tk.Label(t, text='Made by Kevin Huang (kehuang8@gmail.com)').pack(fill=tk.Y)
		tk.Label(t, text='Written in Python').pack(fill=tk.Y)
		tk.Label(t, text='Made using Mayavi and Tkinter').pack(fill=tk.Y)

	def _select_fgcolor(self):
		color = tk.colorchooser.askcolor(initialcolor=eval(self.fgcolor.get()))[0]
		if color:
			color = tuple(int(x) for x in color)
		self.fgcolor.set(str(color))
		
	def _select_bgcolor(self):
		color = tk.colorchooser.askcolor(initialcolor=eval(self.bgcolor.get()))[0]
		if color:
			color = tuple(int(x) for x in color)
		self.bgcolor.set(str(color))

	def add_element(self):
		t = tk.Toplevel()
		x = self.root.winfo_x()
		y = self.root.winfo_y()
		t.geometry('+{0}+{1}'.format(x + 20, y + 20))
		ElementCreator(t, self, self.element_number)

	def add_element_final(self, e):
		f = tk.Frame(self.element_frame)
		e.initialize(f, self)
		self.elements.append(e)

		f.grid(row=self.element_number, column=1, pady=3, columnspan=3, sticky=('e','w'))
		self.element_number += 1

	def redraw_elements(self):
		for i, element in enumerate(self.elements):
			f = element.parent
			f.grid(row=i, column=1, pady=3, columnspan=3, sticky=('e','w'))

	def delete_element(self, e):
		self.elements.remove(e)
		e.parent.destroy()
		self.element_number -= 1
		self.redraw_elements()

	def edit_element(self, e):
		t = tk.Toplevel()
		x = self.root.winfo_x()
		y = self.root.winfo_y()
		t.geometry('+{0}+{1}'.format(x + 20, y + 20))
		ElementEditor(t, self, e)

	def load_file(self, file):
		with open(file, 'rb') as handle:
			info = pickle.load(handle)

		for e in self.elements:
			e.parent.destroy()
		self.elements = []

		for element_info in info:
			name = element_info[0]
			eq_raw = element_info[1]
			if isinstance(eq_raw, list):
				eq = VectorEquation(*eq_raw)
				eq.to_tkVar()
			else:
				eq = tk.StringVar()
				eq.set(eq_raw)
			type_ = element_info[2]
			properties_ = element_info[3]

			e = Element(name, eq, type_, properties_)
			f = tk.Frame(self.element_frame)
			e.initialize(f, self)
			self.elements.append(e)

		self.element_number = len(info) + 1
		self.redraw_elements()

	def open(self):
		file = tk.filedialog.askopenfilename(defaultextension='.FAZFILE')
		if file:
			self.savefile = file
			self.menu_file.entryconfig('Save', state='normal')
			self.load_file(file)

	def save_as(self):
		file = tk.filedialog.asksaveasfilename(defaultextension='.FAZFILE', filetypes=(('FAZFILE', '*.FAZFILE'),) )
		if file:
			self.menu_file.entryconfig('Save', state='normal')
			self.savefile = file
			self.save_file()

	def save_file(self):
		element_infos = [x.info() for x in self.elements]
		with open(self.savefile, 'wb') as handle:
			pickle.dump(element_infos, handle, protocol=pickle.HIGHEST_PROTOCOL)

	def parabola(self):
		p = Parabola()
		p.configure_traits()

	def change_element(self):
		self.redraw_elements()

	def graph(self):
		if self.bgcolor.get():
			self.bgcolor_final = tuple(float(x / 255) for x in eval(self.bgcolor.get()))
			self.bgcolor_final = tuple(1.0 if x > 1.0 else x for x in self.bgcolor_final)
		else:
			self.bgcolor_final = None

		if self.fgcolor.get():
			self.fgcolor_final = tuple(float(x / 255) for x in eval(self.fgcolor.get()))
			self.fgcolor_final = tuple(1.0 if x > 1.0 else x for x in self.fgcolor_final)
		else:
			self.fgcolor_final = None

		if self.savefile:
			name = os.path.splitext(self.savefile)[0]
		else:
			name = 'New Graph'

		mlab.figure(figure=name, fgcolor=self.fgcolor_final, bgcolor=self.bgcolor_final, size=(800,700))

		max_x = -999999
		min_x = 999999
		max_y = -999999
		min_y = 999999
		max_z = -999999
		min_z = 999999
		for e in self.elements:
			if e.hide.get():
				continue
			Grapher(e).graph()
			try:
				min_x = min(min_x, eval(e.properties['bounds'][0]))
				max_x = max(max_x, eval(e.properties['bounds'][1]))
				min_y = min(min_y, eval(e.properties['bounds'][2]))
				max_y = max(max_y, eval(e.properties['bounds'][3]))
				min_z = min(min_z, eval(e.properties['bounds'][4]))
				max_z = max(max_z, eval(e.properties['bounds'][5]))
			except IndexError:
				pass

		ext = [min_x, max_x, min_y, max_y, min_z, max_z]
		if any([True if abs(i) == 999999 else False for i in ext]):
			mlab.axes(nb_labels=7)
		else:
			mlab.axes(nb_labels=5, extent=ext)
		if self.parallel_projection.get():
			mlab.gcf().scene.parallel_projection = True
		else:
			mlab.gcf().scene.parallel_projection = False
		if self.color_legend.get():
			mlab.colorbar(nb_labels=7, orientation='vertical')

		mlab.show()

a = Application(root)
a.root.mainloop()