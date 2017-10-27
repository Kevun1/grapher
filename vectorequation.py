import tkinter as tk

class VectorEquation:
	def __init__(self, P, Q, R):
		self.P = P
		self.Q = Q
		self.R = R

	def to_tkVar(self):
		if not isinstance(self.P, str):
			return

		self.P2 = tk.StringVar()
		self.Q2 = tk.StringVar()
		self.R2 = tk.StringVar()

		self.P2.set(self.P)
		self.Q2.set(self.Q)
		self.R2.set(self.R)

		self.P = self.P2
		self.Q = self.Q2
		self.R = self.R2

	def get(self):
		return [self.P.get(), self.Q.get(), self.R.get()]