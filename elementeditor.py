from collections import defaultdict

import tkinter as tk
from tkinter import ttk
from elementcreator import ElementCreator
from vectorequation import VectorEquation
from verifier import Verifier

import copy

class ElementEditor(ElementCreator):
	"""
	Creates window that allow the user to edit an existing element. Envokes the caller's change_element() method to
	finalize changes
	"""
	def __init__(self, window, main, element):
		self.window = window
		self.main = main
		self.element = element

		self.window.grab_set()

		self.frame = ttk.Frame(self.window, padding=(10, 5, 10, 5))
		self.frame.grid(row=0, column=0)

		self.name = tk.StringVar()
		self.name.set(self.element.name)
		self.properties = copy.deepcopy(self.element.properties)

		self.verifier = Verifier()

		self.create_menu()
		self.create_widgets()
		self.display_widgets()



		self.window.bind('<<Accept>>', self._accept_bindings)

	def create_widgets(self):
		super().create_widgets()
		self.element_type_selector.current(self.element_type_selector['values'].index(self.element.type))
		self.element_type_selector.grid(row=2, column=1, columnspan=2, pady=10, sticky=('e','w'))
		self.select_element_type()

	def create_implicit(self):
		super().create_implicit()
		if self.element.type == 'Implicit':
			self.equation.set(self.element.equation.get())
			b = [x for x in self.properties['bounds']]
			self.xmin.set(b[0])
			self.xmax.set(b[1])
			self.ymin.set(b[2])
			self.ymax.set(b[3])
			self.zmin.set(b[4])
			self.zmax.set(b[5])

	def create_explicit(self):
		super().create_explicit()
		if self.element.type == 'Explicit':
			self.equation.set(self.element.equation.get())
			b = [x for x in self.properties['bounds']]
			self.xmin.set(b[0])
			self.xmax.set(b[1])
			self.ymin.set(b[2])
			self.ymax.set(b[3])
			self.zmin.set(b[4])
			self.zmax.set(b[5])

	def create_parametric_surface(self):
		super().create_parametric_surface()
		if self.element.type == 'Parametric Surface':
			x, y, z = self.element.equation.get()
			self.e1.set(x)
			self.e2.set(y)
			self.e3.set(z)
			b = [x for x in self.properties['bounds']]
			self.umin.set(b[0])
			self.umax.set(b[1])
			self.vmin.set(b[2])
			self.vmax.set(b[3])	

	def create_parametric_curve(self):
		super().create_parametric_curve()
		if self.element.type == 'Parametric Curve':
			x, y, z = self.element.equation.get()
			self.e1.set(x)
			self.e2.set(y)
			self.e3.set(z)
			b = [x for x in self.properties['bounds']]
			self.tmin.set(b[0])
			self.tmax.set(b[1])

	def create_vfield(self):
		super().create_vfield()
		if self.element.type == 'Vector Field':
			P, Q, R = self.element.equation.get()
			if (self.element.properties['cut plane']):
				self.cut_plane.set(self.properties['cut plane'])
			self.e1.set(P)
			self.e2.set(Q)
			self.e3.set(R)
			self.equation = VectorEquation(self.e1, self.e2, self.e3)
			b = [x for x in self.properties['bounds']]
			self.xmin.set(b[0])
			self.xmax.set(b[1])
			self.ymin.set(b[2])
			self.ymax.set(b[3])
			self.zmin.set(b[4])
			self.zmax.set(b[5])

			self.mask_points_scale.set(self.properties['mask points'] * 100)
			self.mask_pts_num.set(self.properties['mask points'] * 100)

			self.scale_factor.set(self.properties['scale factor'])

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

		self.element.change(self.name.get(), self.equation, self.element_type.get(), self.properties)
		self.main.change_element()
		self.exit()