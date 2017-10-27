from collections import defaultdict
import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import *
from vectorequation import VectorEquation
from element import Element
from optionwindow import ResolutionEntryWindow, OpacityWindow
from verifier import Verifier

def nothing():
	return None

class ElementCreator:
	"""
	Creates a new window that allows the user to create an element. Envokes the creator's "add_element_final" method to finalize the element
	"""
	def __init__(self, window, main, number=1):
		"""
		[tk window] window - window on which to draw on
		[Application] main - main app class which creates this window
		[int] number - the nummber the default name this element is assigned
		"""
		self.main = main
		self.window = window
		self.window.grab_set()
		self.window.option_add('*tearOff', tk.FALSE)

		self.frame = ttk.Frame(self.window, padding=(10, 5, 10, 5))
		self.frame.grid(row=0, column=0)

		self.name = tk.StringVar()
		self.name.set("Element " + str(number))

		self.properties = defaultdict(nothing)

		self.create_widgets()
		self.display_widgets()
		self.create_menu()

		self.verifier = Verifier()

		self.window.bind('<<Accept>>', self._accept_bindings)

	def _accept_bindings(self, *args):

		for i in [self._set_scale]:
			try:
				i()
			except:
				pass
	
	def create_widgets(self):
		self.element_name = tk.Entry(self.frame, textvariable=self.name)
		self.element_type = tk.StringVar()
		self.element_type_selector = ttk.Combobox(self.frame, textvariable=self.element_type)
		self.element_type_selector['values'] = ['Implicit', 'Explicit', 'Parametric Surface', 'Parametric Curve', 'Vector Field']
		self.element_type_selector.configure(state='readonly')
		self.element_type_selector.bind('<<ComboboxSelected>>', self.select_element_type)

		self.frame2 = tk.Frame(self.frame)
		self.bounds_frame = tk.Frame(self.frame)

		self.cancel_button = tk.Button(self.frame, text='Cancel', command=self.exit)
		self.accept_button = tk.Button(self.frame, text='Ok', command=self.accept)

	def display_widgets(self):
		self.element_name.grid(row=1, column=1, columnspan=2, pady=10, sticky=('e','w'))
		self.element_type_selector.grid(row=2, column=1, columnspan=2, pady=10, sticky=('e','w'))
		self.frame2.grid(row=3, column=1, rowspan=2, columnspan=4, sticky=('n','s','e','w'))
		self.bounds_frame.grid(row=3, column=5, rowspan=4, columnspan=4, sticky=('n','s','e','w'))
		self.cancel_button.grid(row=8, column=7, padx=5, pady=5, sticky=('n','s','e','w'))
		self.accept_button.grid(row=8, column=8, padx=5, pady=5, sticky=('n','s','e','w'))

		self.window.rowconfigure(0, weight=1)
		self.window.columnconfigure(0, weight=1)

	def create_menu(self):
		self.menubar = tk.Menu(self.window)
		self.window['menu'] = self.menubar

		self.menu_options = tk.Menu(self.menubar)
		self.menu_quickload = tk.Menu(self.menubar)

		self.menubar.add_cascade(menu=self.menu_options, label='Options')
		self.menubar.add_cascade(menu=self.menu_quickload, label='Quick Load Examples')

		self.menubar.entryconfig('Quick Load Examples', state='disabled')

		self.menu_options.add_command(label='Set resolution', command=self.set_resolution)
		self.menu_options.add_command(label='Choose Color', command=self.choose_color)
		self.menu_options.add_command(label='Opacity', command=self.set_opacity)

		self.menu_options.add_separator()

	def set_resolution(self):
		self.window.grab_release()
		t = tk.Toplevel()
		x = self.window.winfo_x()
		y = self.window.winfo_y()
		t.geometry('+{0}+{1}'.format(x + 20, y + 20))
		ResolutionEntryWindow(t, self)

	def set_opacity(self):
		self.window.grab_release()
		t = tk.Toplevel()
		x = self.window.winfo_x()
		y = self.window.winfo_y()
		t.geometry('+{0}+{1}'.format(x + 20, y + 20))
		OpacityWindow(t, self)

	def choose_color(self):
		if self.properties['color']:
			print("COLOR:", self.properties['color'])
			color = tk.colorchooser.askcolor(initialcolor=self.properties['color'])[0]
		else:
			color = tk.colorchooser.askcolor()[0]
		if color:
			color = tuple(int(x) for x in color)
		self.properties['color'] = color

	def select_element_type(self, event=None):
		for widget in self.frame2.winfo_children():
			widget.destroy()
		for widget in self.bounds_frame.winfo_children():
			widget.destroy()
			
		if self.element_type.get() == 'Implicit':
			self.create_implicit()
		elif self.element_type.get() == 'Explicit':
			self.create_explicit()
		elif self.element_type.get() == 'Parametric Surface':
			self.create_parametric_surface()
		elif self.element_type.get() == 'Parametric Curve':
			self.create_parametric_curve()
		elif self.element_type.get() == 'Vector Field':
			self.create_vfield()

	def create_xyz_bounds(self):
		self.bounds_label = tk.Label(self.bounds_frame, text="Bounds")
		self.xmin_label = tk.Label(self.bounds_frame, text="x min")
		self.xmax_label = tk.Label(self.bounds_frame, text="x max")
		self.ymin_label = tk.Label(self.bounds_frame, text="y min")
		self.ymax_label = tk.Label(self.bounds_frame, text="y max")
		self.zmin_label = tk.Label(self.bounds_frame, text="z min")
		self.zmax_label = tk.Label(self.bounds_frame, text="z max")

		self.xmin = tk.StringVar()
		self.xmax = tk.StringVar()
		self.ymin = tk.StringVar()
		self.ymax = tk.StringVar()
		self.zmin = tk.StringVar()
		self.zmax = tk.StringVar()

		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")

		if not self.properties['bounds'] or len(self.properties['bounds']) != 6:
			self._update_bounds_xyz()

		self.xmin.trace('w', self._update_bounds_xyz)
		self.xmax.trace('w', self._update_bounds_xyz)
		self.ymin.trace('w', self._update_bounds_xyz)
		self.ymax.trace('w', self._update_bounds_xyz)
		self.zmin.trace('w', self._update_bounds_xyz)
		self.zmax.trace('w', self._update_bounds_xyz)

		self.xmin_entry = tk.Entry(self.bounds_frame, textvariable=self.xmin)
		self.xmax_entry = tk.Entry(self.bounds_frame, textvariable=self.xmax)
		self.ymin_entry = tk.Entry(self.bounds_frame, textvariable=self.ymin)
		self.ymax_entry = tk.Entry(self.bounds_frame, textvariable=self.ymax)
		self.zmin_entry = tk.Entry(self.bounds_frame, textvariable=self.zmin)
		self.zmax_entry = tk.Entry(self.bounds_frame, textvariable=self.zmax)

		self.xmin_entry.bind('<<Accept>>', lambda *args: self._check_bounds(self.xmin.get()))
		self.xmax_entry.bind('<<Accept>>', lambda *args: self._check_bounds(self.xmax.get()))
		self.ymin_entry.bind('<<Accept>>', lambda *args: self._check_bounds(self.ymin.get()))
		self.ymax_entry.bind('<<Accept>>', lambda *args: self._check_bounds(self.ymax.get()))
		self.zmin_entry.bind('<<Accept>>', lambda *args: self._check_bounds(self.zmin.get()))
		self.zmax_entry.bind('<<Accept>>', lambda *args: self._check_bounds(self.zmax.get()))

		self.bounds_label.grid(row=1, column=1, pady=5, sticky=('e','w'))
		self.xmin_label.grid(row=2, column=1, pady=5, sticky=('e','w'))
		self.xmax_label.grid(row=2, column=3, pady=5, sticky=('e','w'))
		self.ymin_label.grid(row=3, column=1, pady=5, sticky=('e','w'))
		self.ymax_label.grid(row=3, column=3, pady=5, padx=3, sticky=('e','w'))
		self.zmin_label.grid(row=4, column=1, pady=5, padx=3, sticky=('e','w'))
		self.zmax_label.grid(row=4, column=3, pady=5, padx=3, sticky=('e','w'))

		self.xmin_entry.grid(row=2, column=2, pady=5, sticky=('e','w'))
		self.xmax_entry.grid(row=2, column=4, pady=5, sticky=('e','w'))
		self.ymin_entry.grid(row=3, column=2, pady=5, sticky=('e','w'))
		self.ymax_entry.grid(row=3, column=4, pady=5, sticky=('e','w'))
		self.zmin_entry.grid(row=4, column=2, pady=5, sticky=('e','w'))
		self.zmax_entry.grid(row=4, column=4, pady=5, sticky=('e','w'))

	def _update_bounds_xyz(self, *args):
		self.properties['bounds'] = [self.xmin.get(), self.xmax.get(), self.ymin.get(), self.ymax.get(), self.zmin.get(), self.zmax.get()]

	def create_uv_bounds(self):
		self.bounds_label = tk.Label(self.bounds_frame, text="Bounds")
		self.umin_label = tk.Label(self.bounds_frame, text="u min")
		self.umax_label = tk.Label(self.bounds_frame, text="u max")
		self.vmin_label = tk.Label(self.bounds_frame, text="v min")
		self.vmax_label = tk.Label(self.bounds_frame, text="v max")

		self.umin = tk.StringVar()
		self.umax = tk.StringVar()
		self.vmin = tk.StringVar()
		self.vmax = tk.StringVar()

		self.umin.set("-5")
		self.umax.set("5")
		self.vmin.set("-5")
		self.vmax.set("5")

		if not self.properties['bounds'] or len(self.properties['bounds']) != 4:
			self._update_bounds_uv()

		self.umin.trace('w', self._update_bounds_uv)
		self.umax.trace('w', self._update_bounds_uv)
		self.vmin.trace('w', self._update_bounds_uv)
		self.vmax.trace('w', self._update_bounds_uv)

		self.umin_entry = tk.Entry(self.bounds_frame, textvariable=self.umin)
		self.umax_entry = tk.Entry(self.bounds_frame, textvariable=self.umax)
		self.vmin_entry = tk.Entry(self.bounds_frame, textvariable=self.vmin)
		self.vmax_entry = tk.Entry(self.bounds_frame, textvariable=self.vmax)

		self.umin_entry.bind('<<Accept>>', lambda *args: self._check_bounds(self.umin.get()))
		self.umax_entry.bind('<<Accept>>', lambda *args: self._check_bounds(self.umax.get()))
		self.vmin_entry.bind('<<Accept>>', lambda *args: self._check_bounds(self.vmin.get()))
		self.vmax_entry.bind('<<Accept>>', lambda *args: self._check_bounds(self.vmax.get()))

		self.bounds_label.grid(row=1, column=1, pady=5, sticky=('e','w'))
		self.umin_label.grid(row=2, column=1, pady=5, sticky=('e','w'))
		self.umax_label.grid(row=2, column=3, pady=5, sticky=('e','w'))
		self.vmin_label.grid(row=3, column=1, pady=5, sticky=('e','w'))
		self.vmax_label.grid(row=3, column=3, pady=5, padx=3, sticky=('e','w'))

		self.umin_entry.grid(row=2, column=2, pady=5, sticky=('e','w'))
		self.umax_entry.grid(row=2, column=4, pady=5, sticky=('e','w'))
		self.vmin_entry.grid(row=3, column=2, pady=5, sticky=('e','w'))
		self.vmax_entry.grid(row=3, column=4, pady=5, sticky=('e','w'))

	def _update_bounds_uv(self, *args):
		self.properties['bounds'] = [self.umin.get(), self.umax.get(), self.vmin.get(), self.vmax.get()]

	def create_t_bounds(self):
		self.bounds_label = tk.Label(self.bounds_frame, text="Bounds")
		self.tmin_label = tk.Label(self.bounds_frame, text="t min")
		self.tmax_label = tk.Label(self.bounds_frame, text="t max")

		self.tmin = tk.StringVar()
		self.tmax = tk.StringVar()

		self.tmin.set('0')
		self.tmax.set('1')

		if not self.properties['bounds'] or len(self.properties['bounds']) != 2:
			self._update_bounds_t()

		self.tmin.trace('w', self._update_bounds_t)
		self.tmax.trace('w', self._update_bounds_t)

		self.tmin_entry = tk.Entry(self.bounds_frame, textvariable=self.tmin)
		self.tmax_entry = tk.Entry(self.bounds_frame, textvariable=self.tmax)

		self.tmin_entry.bind('<<Accept>>', lambda *args: self._check_bounds(self.tmin.get()))
		self.tmax_entry.bind('<<Accept>>', lambda *args: self._check_bounds(self.tmax.get()))

		self.bounds_label.grid(row=1, column=1, pady=5, sticky=('e','w'))
		self.tmin_label.grid(row=2, column=1, pady=5, sticky=('e','w'))
		self.tmax_label.grid(row=2, column=3, pady=5, sticky=('e','w'))

		self.tmin_entry.grid(row=2, column=2, pady=5, sticky=('e','w'))
		self.tmax_entry.grid(row=2, column=4, pady=5, sticky=('e','w'))

	def _update_bounds_t(self, *args):
		self.properties['bounds'] = [self.tmin.get(), self.tmax.get()]

	def create_implicit(self):
		self.description = tk.Label(self.frame2, text="Enter a function in the form F(x, y, z) = 0")

		self.equation = tk.StringVar()
		self.equation_entry = tk.Entry(self.frame2, width=50, textvariable=self.equation)
		self.equation_entry.bind('<<Accept>>', lambda *args: self._check_equation(self.equation.get()))

		self.equals_zero = tk.Label(self.frame2, text="= 0")

		self.description.grid(row=1, column=1, columnspan=3, pady=5, sticky=('e','w'))
		self.equation_entry.grid(row=2, column=1, columnspan=3, pady=5, sticky=('e','w'))
		self.equals_zero.grid(row=2, column=4, pady=5, sticky=('w'))

		self.create_xyz_bounds()
		self._create_implicit_menu()

	def _create_implicit_menu(self):
		self._delete_other_menu_options()

		self.implicit_gradient_menu = tk.Menu(self.menu_options)
		self.menu_options.add_cascade(menu=self.implicit_gradient_menu, label='Gradient Field')

		self._handle_gradient(self.implicit_gradient_menu)

		self._quickload_implicit()

	def _update_gradient(self, *args):
		self.properties['gradient'] = self.gradient.get()
		if self.properties['gradient'] == 'None':
			self.properties['gradient'] = None

	def _handle_gradient(self, menu):
		self.gradient = tk.StringVar()
		self.gradient.trace('w', self._update_gradient)
		if self.properties['gradient'] != None:
			self.gradient.set(self.properties['gradient'])
		else:
			self.gradient.set('None')

		menu.add_radiobutton(label='None', variable=self.gradient, value='')
		menu.add_radiobutton(label='Show Gradient Vector Field and Surface', variable=self.gradient, value='gradient and surface')
		menu.add_radiobutton(label='Show Gradient Vector Field only', variable=self.gradient, value='gradient only')

	def _quickload_implicit(self):
		self._delete_other_quickloads()

		self.menubar.entryconfig('Quick Load Examples', state='normal')

		self.menu_quickload.add_command(label='Sphere', command=self._sphere)
		self.menu_quickload.add_command(label='Elliptical Paraboloid', command=self._elliptical_paraboloid)
		self.menu_quickload.add_command(label='Hyperbolic Paraboloid', command=self._hyperbolic_paraboloid)
		self.menu_quickload.add_command(label='Ellipsoid', command=self._ellipsoid)
		self.menu_quickload.add_command(label='Plane', command=self._plane)
		self.menu_quickload.add_command(label='Cone', command=self._cone)
		self.menu_quickload.add_command(label='Hyperboloid of One Sheet', command=self._hyperboloid_one_sheet)
		self.menu_quickload.add_command(label='Hyperboloid of Two Sheets', command=self._hyperboloid_two_sheet)
		self.menu_quickload.add_command(label='Teardrop', command=self._teardrop)
		self.menu_quickload.add_command(label='Weird Thing', command=self._weird_thing)
		self.menu_quickload.add_command(label='Heart', command=self._heart)

	def _sphere(self):
		self.equation.set('x^2+y^2+z^2-4')
		self.xmin.set("-2")
		self.xmax.set("2")
		self.ymin.set("-2")
		self.ymax.set("2")
		self.zmin.set("-2")
		self.zmax.set("2")

	def _elliptical_paraboloid(self):
		self.equation.set('x^2+y^2-z')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("0")
		self.zmax.set("5")

	def _hyperbolic_paraboloid(self):
		self.equation.set('x^2-y^2-z')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")

	def _ellipsoid(self):
		self.equation.set('4*x^2+8*y^2+2*z^2-1')
		self.xmin.set("-1")
		self.xmax.set("1")
		self.ymin.set("-1")
		self.ymax.set("1")
		self.zmin.set("-1")
		self.zmax.set("1")

	def _plane(self):
		self.equation.set('x+y+3*z-2')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")

	def _cone(self):
		self.equation.set('x^2+y^2-z^2')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")

	def _hyperboloid_one_sheet(self):
		self.equation.set('x^2+y^2-z^2-1')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")

	def _hyperboloid_two_sheet(self):
		self.equation.set('x^2-y^2-z^2-1')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")

	def _teardrop(self):
		self.equation.set('x^2+y^2-(1-z)*z^3')
		self.xmin.set("-0.4")
		self.xmax.set("0.4")
		self.ymin.set("-0.4")
		self.ymax.set("0.4")
		self.zmin.set("0")
		self.zmax.set("1")

	def _weird_thing(self):
		self.equation.set('cos(x) + cos(y) + cos(z)')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")

	def _heart(self):
		self.equation.set('(x^2 + (9 *y^2) / 4 + z^2 - 1)^3 - x^2*z^3 - (9 *y^2 * z^3) / 80')
		self.xmin.set("-3")
		self.xmax.set("3")
		self.ymin.set("-3")
		self.ymax.set("3")
		self.zmin.set("-3")
		self.zmax.set("3")

	def create_explicit(self):
		self.description = tk.Label(self.frame2, text="Enter a function in the form z = F(x, y)")

		self.equation = tk.StringVar()
		self.equation_entry = tk.Entry(self.frame2, width=50, textvariable=self.equation)
		self.equation_entry.bind('<<Accept>>', lambda *args: self._check_equation(self.equation.get()))

		self.zequals = tk.Label(self.frame2, text="z =")

		self.description.grid(row=1, column=1, columnspan=3, pady=5, sticky=('e','w'))
		self.equation_entry.grid(row=2, column=2, columnspan=3, pady=5, sticky=('e','w'))
		self.zequals.grid(row=2, column=1, pady=5, sticky=('e','w'))

		self.create_xyz_bounds()
		self._create_explicit_menu()

	def _create_explicit_menu(self):
		self._delete_other_menu_options()
		"""
		self.explicit_gradient_menu = tk.Menu(self.menu_options)
		self.menu_options.add_cascade(menu=self.explicit_gradient_menu, label='Gradient Field')

		self._handle_gradient(self.explicit_gradient_menu)
		"""

		self.representation_menu = tk.Menu(self.menu_options)
		self.menu_options.add_cascade(menu=self.representation_menu, label='View as')

		self._handle_representation(self.representation_menu)

		self.level_curve_options = tk.Menu(self.menu_options)
		self.menu_options.add_cascade(menu=self.level_curve_options, label='Level Curves')

		self._show_level_curves = tk.StringVar()
		self._show_level_curves.trace('w', self._update_level_curves)
		if self.properties['level curves'] != None:
			self._show_level_curves.set(self.properties['level curves'])
		else:
			self._show_level_curves.set('')
		self.level_curve_options.add_radiobutton(label='None', variable=self._show_level_curves, value='')
		self.level_curve_options.add_radiobutton(label='Show Level Curves and Surface', variable=self._show_level_curves, value='show both')
		self.level_curve_options.add_radiobutton(label='Show Level Curves only', variable=self._show_level_curves, value='show one')

		self._quickload_explicit()

	def _update_level_curves(self, *args):
		self.properties['level curves'] = self._show_level_curves.get()
		if self.properties['level curves'] == 'None':
			self.properties['level curves'] = None

	def _handle_representation(self, menu):
		self.representation = tk.StringVar()
		self.representation.trace('w', self._update_representation)
		if self.properties['representation'] != None:
			self.representation.set(self.properties['representation'])
		else:
			self.representation.set('None')

		menu.add_radiobutton(label='Smooth Surface (default)', variable=self.representation, value='surface')
		menu.add_radiobutton(label='Wireframe', variable=self.representation, value='wireframe')
		menu.add_radiobutton(label='Points', variable=self.representation, value='points')

	def _update_representation(self, *args):
			self.properties['representation'] = self.representation.get()
			if self.properties['representation'] == 'None':
				self.properties['representation'] = None

	def _quickload_explicit(self):
		self._delete_other_quickloads()

		self.menubar.entryconfig('Quick Load Examples', state='normal')

		self.menu_quickload.add_command(label='Elliptical Paraboloid', command=self._elliptical_paraboloid_exp)
		self.menu_quickload.add_command(label='Ripple', command=self._ripple)
		self.menu_quickload.add_command(label='Bumps', command=self._bumps)
		self.menu_quickload.add_command(label='Pyramid', command=self._pyramid)

	def _elliptical_paraboloid_exp(self):
		self.equation.set('x^2+y^2')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("0")
		self.zmax.set("5")		

	def _ripple(self):
		self.equation.set('sin(x^2+y^2)')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")

	def _bumps(self):
		self.equation.set('3*sin(x)*cos(y)')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")

	def _pyramid(self):
		self.equation.set('1 - abs(x+y) - abs(y - x)')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")

	def create_parametric_surface(self):
		self.description = tk.Label(self.frame2, text="Enter a function where x, y, and z are functions of the parameters u and v")

		self.e1 = tk.StringVar()
		self.e2 = tk.StringVar()
		self.e3 = tk.StringVar()

		self.e1_entry = tk.Entry(self.frame2, width=50, textvariable=self.e1)
		self.e2_entry = tk.Entry(self.frame2, width=50, textvariable=self.e2)
		self.e3_entry = tk.Entry(self.frame2, width=50, textvariable=self.e3)

		self.e1_entry.bind('<<Accept>>', lambda *args: self._check_equation(self.e1.get()))
		self.e2_entry.bind('<<Accept>>', lambda *args: self._check_equation(self.e2.get()))
		self.e3_entry.bind('<<Accept>>', lambda *args: self._check_equation(self.e3.get()))

		self.equation = VectorEquation(self.e1, self.e2, self.e3)

		self.xequals = tk.Label(self.frame2, text="x =")
		self.yequals = tk.Label(self.frame2, text="y =")
		self.zequals = tk.Label(self.frame2, text="z =")

		self.description.grid(row=1, column=1, columnspan=3, pady=5, sticky=('e','w'))
		self.e1_entry.grid(row=2, column=2, columnspan=3, pady=5, sticky=('e','w'))
		self.e2_entry.grid(row=3, column=2, columnspan=3, pady=5, sticky=('e','w'))
		self.e3_entry.grid(row=4, column=2, columnspan=3, pady=5, sticky=('e','w'))
		self.xequals.grid(row=2, column=1, pady=5, sticky=('e','w'))
		self.yequals.grid(row=3, column=1, pady=5, sticky=('e','w'))
		self.zequals.grid(row=4, column=1, pady=5, sticky=('e','w'))

		self.create_uv_bounds()
		self._create_parametric_surface_menu()

	def _create_parametric_surface_menu(self):
		self._delete_other_menu_options()

		self.representation_menu = tk.Menu(self.menu_options)
		self.menu_options.add_cascade(menu=self.representation_menu, label='View as')

		self._handle_representation(self.representation_menu)

		self.representation_menu.add_radiobutton(label='Mesh', variable=self.representation, value='mesh')
		self.representation_menu.add_radiobutton(label='Fancy Mesh', variable=self.representation, value='fancymesh')

		self._quickload_parametric_surface()

	def _quickload_parametric_surface(self):
		self._delete_other_quickloads()

		self.menubar.entryconfig('Quick Load Examples', state='normal')

		self.menu_quickload.add_command(label='Sphere', command=self._sphere_para)
		self.menu_quickload.add_command(label='Mobius Strip', command=self._mobius_strip)
		self.menu_quickload.add_command(label='Boy\'s Surface', command=self._boy_surface)
		self.menu_quickload.add_command(label='Torus', command=self._torus)
		self.menu_quickload.add_command(label='Seashell', command=self._seashell)
		self.menu_quickload.add_command(label='Klein\'s Bottle', command=self._klein_bottle)

	def _sphere_para(self):
		self.umin.set("0")
		self.umax.set("2*pi")
		self.vmin.set("0")
		self.vmax.set("pi")
		self.e1.set('sin(v)*cos(u)')
		self.e2.set('sin(v)*sin(u)')
		self.e3.set('cos(v)')

	def _mobius_strip(self):
		self.umin.set("0")
		self.umax.set("2*pi")
		self.vmin.set("-1")
		self.vmax.set("1")
		self.e1.set('(1 + (v/2) * cos(u/2))*cos(u)')
		self.e2.set('(1 + (v/2) * cos(u/2))*sin(u)')
		self.e3.set('(v/2)*sin(u/2)')

	def _boy_surface(self):
		self.umin.set("0")
		self.umax.set("pi")
		self.vmin.set("0")
		self.vmax.set("pi")
		self.e1.set('2 / 3 * (cos(u) * cos(2 * v)  + sqrt(2) * sin(u) * cos(v)) * cos(u) / (sqrt(2) - sin(2 * u) * sin(3 * v))')
		self.e2.set('2 / 3 * (cos(u) * sin(2 * v) -  sqrt(2) * sin(u) * sin(v)) * cos(u) / (sqrt(2) - sin(2 * u) * sin(3 * v))')
		self.e3.set('-sqrt(2) * cos(u) * cos(u) / (sqrt(2) - sin(2 * u) * sin(3 * v))')		

	def _torus(self):
		self.umin.set("0")
		self.umax.set("2*pi")
		self.vmin.set("0")
		self.vmax.set("2*pi")
		self.e1.set('(4 + 2*cos(v))*cos(u)')
		self.e2.set('(4 + 2*cos(v))*sin(u)')
		self.e3.set('2*sin(v)')		

	def _seashell(self):
		self.umin.set("0")
		self.umax.set("6*pi")
		self.vmin.set("0")
		self.vmax.set("6*pi")
		self.e1.set('2*(1-exp(u/(6*pi))) * cos(u) * cos(v/2)^2')
		self.e2.set('2*(-1+exp(u/(6*pi))) * sin(u) * cos(v/2)^2')
		self.e3.set('1-exp(u/(3*pi)) - sin(v) + exp(u/(6*pi)) * sin(v)')	

	def _klein_bottle(self):
		self.umin.set("0")
		self.umax.set("pi")
		self.vmin.set("0")
		self.vmax.set("2*pi")
		self.e1.set('-(2/15)*cos(u)*(3*cos(v)-30*sin(u)+90*cos(u)^4*sin(u)-60*cos(u)^6*sin(u)+5*cos(u)*cos(v)*sin(u))')
		self.e2.set('''-(1/15)*sin(u)*(3*cos(v)-3*cos(u)^2*cos(v)-48*cos(u)^4*cos(v)+48*cos(u)^6.*cos(v)-60*sin(u)+5*cos(u)*cos(v)*sin(u)-5*cos(u)^3.*cos(v)*sin(u)
			-80*cos(u)^5*cos(v)*sin(u)+ 80*cos(u)^7*cos(v)*sin(u))''')
		self.e3.set('(2/15)*(3+5*cos(u)*sin(u))*sin(v)')			

	def create_parametric_curve(self):
		self.description = tk.Label(self.frame2, text="Enter a function where x, y, and z are functions of a parameter t")

		self.e1 = tk.StringVar()
		self.e2 = tk.StringVar()
		self.e3 = tk.StringVar()

		self.e1_entry = tk.Entry(self.frame2, width=50, textvariable=self.e1)
		self.e2_entry = tk.Entry(self.frame2, width=50, textvariable=self.e2)
		self.e3_entry = tk.Entry(self.frame2, width=50, textvariable=self.e3)

		self.e1_entry.bind('<<Accept>>', lambda *args: self._check_equation(self.e1.get()))
		self.e2_entry.bind('<<Accept>>', lambda *args: self._check_equation(self.e2.get()))
		self.e3_entry.bind('<<Accept>>', lambda *args: self._check_equation(self.e3.get()))

		self.equation = VectorEquation(self.e1, self.e2, self.e3)

		self.xequals = tk.Label(self.frame2, text="x =")
		self.yequals = tk.Label(self.frame2, text="y =")
		self.zequals = tk.Label(self.frame2, text="z =")

		self.description.grid(row=1, column=1, columnspan=3, pady=5, sticky=('e','w'))
		self.e1_entry.grid(row=2, column=2, columnspan=3, pady=5, sticky=('e','w'))
		self.e2_entry.grid(row=3, column=2, columnspan=3, pady=5, sticky=('e','w'))
		self.e3_entry.grid(row=4, column=2, columnspan=3, pady=5, sticky=('e','w'))
		self.xequals.grid(row=2, column=1, pady=5, sticky=('e','w'))
		self.yequals.grid(row=3, column=1, pady=5, sticky=('e','w'))
		self.zequals.grid(row=4, column=1, pady=5, sticky=('e','w'))

		self.create_t_bounds()
		self._create_parametric_curve_menu()

	def _create_parametric_curve_menu(self):
		self._delete_other_menu_options()

		self.parametric_gradient_menu = tk.Menu(self.menu_options)
		self.menu_options.add_cascade(menu=self.parametric_gradient_menu, label='Gradient Field')

		self._quickload_parametric_curve()

	def _quickload_parametric_curve(self):
		self._delete_other_quickloads()

		self.menubar.entryconfig('Quick Load Examples', state='normal')

		self.menu_quickload.add_command(label='Spiral', command=self._spiral)
		self.menu_quickload.add_command(label='Loop Thing', command=self._loop_thing_1)
		self.menu_quickload.add_command(label='Line', command=self._line)
		self.menu_quickload.add_command(label='Random Curve', command=self._random_curve)

	def _spiral(self):
		self.tmin.set("0")
		self.tmax.set("2*pi")
		self.e1.set('cos(4*t)')
		self.e2.set('sin(4*t)')
		self.e3.set('t')	

	def _loop_thing_1(self):
		self.tmin.set('0')
		self.tmax.set('2*pi')
		self.e1.set('2*sin(3*t)*cos(t)')
		self.e2.set('2*sin(3*t)*sin(t)')
		self.e3.set('sin(3*t)')

	def _line(self):
		self.tmin.set('0')
		self.tmax.set('1')
		self.e1.set('-1+2*t')
		self.e2.set('3-t')
		self.e3.set('3*t')

	def _random_curve(self):
		self.tmin.set('0')
		self.tmax.set('2*pi')
		self.e1.set('cos(t)*(1 - (t/2))')
		self.e2.set('sin(t)*(1 - (t/2))')
		self.e3.set('1 - sin(t)*cos(t)')

	def create_vfield(self):
		self.description = tk.Label(self.frame2, text="Enter a vector function F = <P(x, y, z), Q(x, y, z), R(x, y, z)>")

		self.e1 = tk.StringVar()
		self.e2 = tk.StringVar()
		self.e3 = tk.StringVar()

		self.e1_entry = tk.Entry(self.frame2, width=50, textvariable=self.e1)
		self.e2_entry = tk.Entry(self.frame2, width=50, textvariable=self.e2)
		self.e3_entry = tk.Entry(self.frame2, width=50, textvariable=self.e3)

		self.e1_entry.bind('<<Accept>>', lambda *args: self._check_equation(self.e1.get()))
		self.e2_entry.bind('<<Accept>>', lambda *args: self._check_equation(self.e2.get()))
		self.e3_entry.bind('<<Accept>>', lambda *args: self._check_equation(self.e3.get()))

		self.equation = VectorEquation(self.e1, self.e2, self.e3)

		self.pequals = tk.Label(self.frame2, text="P =")
		self.qequals = tk.Label(self.frame2, text="Q =")
		self.requals = tk.Label(self.frame2, text="R =")

		self.description.grid(row=1, column=1, columnspan=3, pady=5, sticky=('e','w'))
		self.e1_entry.grid(row=2, column=2, columnspan=3, pady=5, sticky=('e','w'))
		self.e2_entry.grid(row=3, column=2, columnspan=3, pady=5, sticky=('e','w'))
		self.e3_entry.grid(row=4, column=2, columnspan=3, pady=5, sticky=('e','w'))
		self.pequals.grid(row=2, column=1, pady=5, sticky=('e','w'))
		self.qequals.grid(row=3, column=1, pady=5, sticky=('e','w'))
		self.requals.grid(row=4, column=1, pady=5, sticky=('e','w'))

		self.cut_plane = tk.BooleanVar()
		self.check_cutplane = ttk.Checkbutton(self.frame2, text="Cut Plane", variable=self.cut_plane, command=self._update_cut_plane, onvalue=True, offvalue=False)
		self.check_cutplane.grid(row=5, column=1, sticky=('n','e','w','s'))

		self.scale_label = tk.Label(self.frame2, text="Scale Factor: ")
		self.scale_label.grid(row=5, column=2, sticky=('e'))

		self.scale_factor = tk.DoubleVar()
		self.scale_factor.set(0.15)

		self.scale_factor_entry = tk.Entry(self.frame2, width=20, textvariable=self.scale_factor)
		self.scale_factor_entry.grid(row=5, column=3, sticky=('e','w'))
		self.scale_factor_entry.bind('<Return>', self._set_scale)
		self.scale_factor_entry.bind('<FocusOut>', self._set_scale)

		self.min_mask = 0.05
		self.max_mask = 0.4

		self.mask_points = tk.DoubleVar()
		self.mask_points_scale = tk.Scale(self.frame2, orient=tk.HORIZONTAL, label='Mask Points (%)', resolution=0.01, length=250, from_=self.min_mask, to=self.max_mask, 
			variable=self.mask_points, command=self._update_maskpts_box, tickinterval=0.07)
		self.mask_points_scale.grid(row=6, column=1, columnspan=2, sticky=('n','e','s','w'))

		self.mask_pts_num = tk.DoubleVar()
		self.mask_pts_entry = tk.Entry(self.frame2, width=20, textvariable=self.mask_pts_num)
		self.mask_pts_num.trace('w', self._update_maskpts_slider)
		self.mask_pts_entry.grid(row=6, column=3, sticky=('w','e'))

		if not self.properties['mask points']:
			self.mask_points_scale.set(0.2)
			self.mask_pts_num.set(0.2)

		self.create_xyz_bounds()
		self._create_vfield_menu()

	def _create_vfield_menu(self):
		self._delete_other_menu_options()

		self.vfield_modify = tk.Menu(self.menu_options)
		self.menu_options.add_cascade(menu=self.vfield_modify, label='Vector Operation')

		self.vfield_normalize = tk.Menu(self.menu_options)
		self.menu_options.add_cascade(menu=self.vfield_normalize, label='Scaling')

		self.vector_operation = tk.StringVar()
		self.vector_operation.trace('w', self._update_vector_operation)
		if self.properties['vector operation'] != None:
			self.vector_operation.set(self.properties['vector operation'])
		self.vfield_modify.add_radiobutton(label='None', variable=self.vector_operation, value='')
		self.vfield_modify.add_radiobutton(label='Curl', variable=self.vector_operation, value='curl')
		#self.vfield_modify.add_radiobutton(label='Divergence', variable=self.vector_operation, value='divergence')

		self.normalize = tk.StringVar()
		self.normalize.trace('w', self._update_normalize)
		if self.properties['normalize'] != None:
			self.normalize.set(self.properties['normalize'])
		self.vfield_normalize.add_radiobutton(label='None', variable=self.normalize, value='')
		self.vfield_normalize.add_radiobutton(label='Normalize', variable=self.normalize, value='normalize')
		self.vfield_normalize.add_radiobutton(label='Flatten', variable=self.normalize, value='flatten')

		self.colormap_options = tk.Menu(self.menu_options)
		self.menu_options.add_cascade(menu=self.colormap_options, label='Color Gradient')

		self.colormap = tk.StringVar()
		self.colormap.trace('w', self._update_colormap)
		if self.properties['colormap'] != None:
			self.colormap.set(self.properties['colormap'])

		self.colormap_options.add_radiobutton(label='Blue-Red (default)', variable=self.colormap, value='blue-red')

		self.colormap_options.add_radiobutton(label='Black-White', variable=self.colormap, value='black-white')
		self.colormap_options.add_radiobutton(label='White-Black', variable=self.colormap, value='binary')

		self.colormap_options.add_radiobutton(label='Grays', variable=self.colormap, value='Greys')
		self.colormap_options.add_radiobutton(label='Brown-BlueGreen', variable=self.colormap, value='BrBG')

		self.colormap_options.add_radiobutton(label='Blues', variable=self.colormap, value='Blues')
		self.colormap_options.add_radiobutton(label='Blue-Green', variable=self.colormap, value='BuGn')
		self.colormap_options.add_radiobutton(label='Blue-Purple', variable=self.colormap, value='BuPu')
		self.colormap_options.add_radiobutton(label='Blue-White_Red', variable=self.colormap, value='bwr')

		self.colormap_options.add_radiobutton(label='Reds', variable=self.colormap, value='Reds')
		self.colormap_options.add_radiobutton(label='Red-Blue', variable=self.colormap, value='RdBu')
		self.colormap_options.add_radiobutton(label='Red-Gray', variable=self.colormap, value='RdGy')
		self.colormap_options.add_radiobutton(label='Red-Purple', variable=self.colormap, value='RdPu')
		self.colormap_options.add_radiobutton(label='Red-Yellow-Blue', variable=self.colormap, value='RdYlBu')
		self.colormap_options.add_radiobutton(label='Red-Yellow-Green', variable=self.colormap, value='RdYlGn')

		self.colormap_options.add_radiobutton(label='Greens', variable=self.colormap, value='Greens')
		self.colormap_options.add_radiobutton(label='Green-Blue', variable=self.colormap, value='GnBu')

		self.colormap_options.add_radiobutton(label='Oranges', variable=self.colormap, value='Oranges')
		self.colormap_options.add_radiobutton(label='Orange-Red', variable=self.colormap, value='OrRd')

		self.colormap_options.add_radiobutton(label='Pink', variable=self.colormap, value='pink')
		self.colormap_options.add_radiobutton(label='Pink-Green', variable=self.colormap, value='PiYG')
		
		self.colormap_options.add_radiobutton(label='Purples', variable=self.colormap, value='Purples')
		self.colormap_options.add_radiobutton(label='Purple-Blue', variable=self.colormap, value='PuBu')
		self.colormap_options.add_radiobutton(label='Purple-Blue-Green', variable=self.colormap, value='PuBuGn')
		self.colormap_options.add_radiobutton(label='Purple-Orange', variable=self.colormap, value='PuOr')
		self.colormap_options.add_radiobutton(label='Purple-Red', variable=self.colormap, value='PuRd')
		self.colormap_options.add_radiobutton(label='Purple-Green', variable=self.colormap, value='PrGn')
		
		self.colormap_options.add_radiobutton(label='Yellow-Green', variable=self.colormap, value='YlGn')
		self.colormap_options.add_radiobutton(label='Yellow-Green-Blue', variable=self.colormap, value='YlGnBu')
		self.colormap_options.add_radiobutton(label='Yellow-Orange-Brown', variable=self.colormap, value='YlOrBr')
		self.colormap_options.add_radiobutton(label='Yellow-Orange-Red', variable=self.colormap, value='YlOrRd')

		self.colormap_options.add_radiobutton(label='Hot', variable=self.colormap, value='hot')
		self.colormap_options.add_radiobutton(label='Cool', variable=self.colormap, value='cool')
		self.colormap_options.add_radiobutton(label='Magma', variable=self.colormap, value='magma')
		self.colormap_options.add_radiobutton(label='Ocean', variable=self.colormap, value='ocean')
		self.colormap_options.add_radiobutton(label='Plasma', variable=self.colormap, value='plasma')
		self.colormap_options.add_radiobutton(label='Terrain', variable=self.colormap, value='terrain')
		self.colormap_options.add_radiobutton(label='Earth', variable=self.colormap, value='earth')
		self.colormap_options.add_radiobutton(label='Wistia', variable=self.colormap, value='Wistia')
		self.colormap_options.add_radiobutton(label='Bone', variable=self.colormap, value='bone')

		self.colormap_options.add_radiobutton(label='Winter', variable=self.colormap, value='winter')
		self.colormap_options.add_radiobutton(label='Autumn', variable=self.colormap, value='autumn')
		self.colormap_options.add_radiobutton(label='Summer', variable=self.colormap, value='summer')
		self.colormap_options.add_radiobutton(label='Spring', variable=self.colormap, value='spring')

		self.colormap_options.add_radiobutton(label='Rainbow', variable=self.colormap, value='rainbow')
		self.colormap_options.add_radiobutton(label='Prism', variable=self.colormap, value='prism')
		self.colormap_options.add_radiobutton(label='Seismic', variable=self.colormap, value='seismic')
		self.colormap_options.add_radiobutton(label='Spectral', variable=self.colormap, value='Spectral')
		self.colormap_options.add_radiobutton(label='Paired', variable=self.colormap, value='paired')

		self._quickload_vfield()

	def _quickload_vfield(self):
		self._delete_other_quickloads()

		self.menubar.entryconfig('Quick Load Examples', state='normal')

		self.menu_quickload.add_command(label='Example 1', command=self._vfieldex1)
		self.menu_quickload.add_command(label='Example 2', command=self._vfieldex2)
		self.menu_quickload.add_command(label='Example 3', command=self._vfieldex3)
		self.menu_quickload.add_command(label='Example 4', command=self._vfieldex4)
		self.menu_quickload.add_command(label='Example 5', command=self._vfieldex5)

	def _vfieldex1(self):
		self.scale_factor.set(0.15)
		self.mask_points.set(0.2)
		self._update_maskpts_box()
		self.colormap.set('blue-red')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")
		self.e1.set('x')
		self.e2.set('y')
		self.e3.set('z')

	def _vfieldex2(self):
		self.scale_factor.set(0.3)
		self.mask_points.set(0.2)
		self._update_maskpts_box()
		self.colormap.set('blue-red')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")
		self.e1.set('y')
		self.e2.set('-x')
		self.e3.set('x*y*z')
		self.normalize.set('flatten')

	def _vfieldex3(self):
		self.scale_factor.set(0.1)
		self.mask_points.set(0.2)
		self._update_maskpts_box()
		self.colormap.set('blue-red')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")
		self.e1.set('x^2+y')
		self.e2.set('z')
		self.e3.set('2*y')

	def _vfieldex4(self):
		self.scale_factor.set(0.15)
		self.mask_points.set(0.2)
		self._update_maskpts_box()
		self.colormap.set('blue-red')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")
		self.e1.set('z')
		self.e2.set('x')
		self.e3.set('y')

	def _vfieldex5(self):
		self.scale_factor.set(0.15)
		self.mask_points.set(0.2)
		self._update_maskpts_box()
		self.colormap.set('blue-red')
		self.xmin.set("-5")
		self.xmax.set("5")
		self.ymin.set("-5")
		self.ymax.set("5")
		self.zmin.set("-5")
		self.zmax.set("5")
		self.e1.set('x^2')
		self.e2.set('-3*x*y')
		self.e3.set('12*z')
		self.normalize.set('flatten')

	def _update_vector_operation(self, *args):
		self.properties['vector operation'] = self.vector_operation.get()
		if self.properties['vector operation'] == 'None':
			self.properties['vector operation'] = None

	def _update_normalize(self, *args):
		self.properties['normalize'] = self.normalize.get()

	def _update_colormap(self, *args):
		self.properties['color'] = None
		self.properties['colormap'] = self.colormap.get()

	def _set_scale(self, *args):
		try:
			v = self.scale_factor.get()
		except:
			self.scale_factor.set(0.15)
		else:
			if v > 2.5:
				self.scale_factor.set(2.5)
			elif v <= 0:
				self.scale_factor.set(0.1)

		self.properties['scale factor'] = self.scale_factor.get()

	def _update_maskpts_slider(self, *args):
		try:
			v = self.mask_pts_num.get()
		except:
			return
		if (v <= self.max_mask and v >= self.min_mask):
			self.mask_points_scale.set(v)
			self.properties['mask points'] = self.mask_points.get() / 100

	def _update_maskpts_box(self, *args):
		self.mask_pts_num.set(self.mask_points.get())
		self.properties['mask points'] = self.mask_points.get() / 100

	def _update_cut_plane(self):
		self.properties['cut plane'] = self.cut_plane.get()

	def _delete_other_menu_options(self):
		for i in range(self.menu_options.index("end") + 1):
			if self.menu_options.type(i) == "separator":
				delete = i
				break

		self.menu_options.delete(delete + 1, 'end')		

	def _delete_other_quickloads(self):
		if self.menu_quickload.index("end") == None:
			return
		self.menu_quickload.delete(0, 'end')

	def _check_equation(self, eq):
		valid = self.verifier.verify(self.element_type.get(), eq)
		if not valid:
			self._invalid_warning(eq)

	def _check_bounds(self, bound):
		valid = self.verifier.check_bounds(bound)
		if not valid:
			self._invalid_warning(bound)

	def _invalid_warning(self, eq):
		self.invalid_list.append(eq)
		self.invalid = True

	def propagate_accept(self):
		self.invalid_list = []
		if self.element_type.get() == 'Implicit' or self.element_type.get() == 'Explicit':
			self.equation_entry.event_generate('<<Accept>>')
			self.xmin_entry.event_generate('<<Accept>>') 
			self.xmax_entry.event_generate('<<Accept>>')
			self.ymin_entry.event_generate('<<Accept>>')
			self.ymax_entry.event_generate('<<Accept>>')
			self.zmin_entry.event_generate('<<Accept>>')
			self.zmax_entry.event_generate('<<Accept>>')
		elif self.element_type.get() == 'Parametric Surface':
			self.e1_entry.event_generate('<<Accept>>')
			self.e2_entry.event_generate('<<Accept>>')
			self.e3_entry.event_generate('<<Accept>>')
			self.umin_entry.event_generate('<<Accept>>')
			self.umax_entry.event_generate('<<Accept>>')
			self.vmin_entry.event_generate('<<Accept>>')
			self.vmax_entry.event_generate('<<Accept>>')
		elif self.element_type.get() == 'Parametric Curve':
			self.e1_entry.event_generate('<<Accept>>')
			self.e2_entry.event_generate('<<Accept>>')
			self.e3_entry.event_generate('<<Accept>>')
			self.tmin_entry.event_generate('<<Accept>>')
			self.tmax_entry.event_generate('<<Accept>>')
		elif self.element_type.get() == 'Vector Field':
			self.e1_entry.event_generate('<<Accept>>')
			self.e2_entry.event_generate('<<Accept>>')
			self.e3_entry.event_generate('<<Accept>>')
			self.xmin_entry.event_generate('<<Accept>>') 
			self.xmax_entry.event_generate('<<Accept>>')
			self.ymin_entry.event_generate('<<Accept>>')
			self.ymax_entry.event_generate('<<Accept>>')
			self.zmin_entry.event_generate('<<Accept>>')
			self.zmax_entry.event_generate('<<Accept>>')

		try:
			self.invalid
		except AttributeError:
			return

		t = tk.Toplevel()
		x = self.window.winfo_x()
		y = self.window.winfo_y()
		t.geometry('+{0}+{1}'.format(x + 35, y + 35))
		t.grab_set()
		tk.Label(t, text='Syntax Error: \n {0}'.format(str(self.invalid_list))).pack(fill=tk.Y)
		def exit_():
			t.grab_release()
			t.destroy()
			self.window.grab_set()
		tk.Button(t, text="Ok", command=exit_).pack(fill=tk.Y)
		t.protocol("WM_DELETE_WINDOW", exit_)

	def accept(self):
		self.window.event_generate('<<Accept>>')
		self.propagate_accept()

		try:
			self.invalid
		except AttributeError:
			pass
		else:
			del self.invalid
			return

		e = Element(self.name.get(), self.equation, self.element_type.get(), self.properties)
		self.main.add_element_final(e)
		self.exit()

	def exit(self):
		self.window.grab_release()
		self.window.destroy()