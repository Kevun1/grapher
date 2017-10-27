import py_expression_eval as pexpr
import random
from numpy import pi, sin, cos, tan, arcsin, arccos, arctan, exp, log, log10, log2, power, sqrt, sign, absolute

class Verifier:
	def __init__(self):
		self.parser = pexpr.Parser()

	def verify(self, eq_type, equation):
		if not self.acceptable(equation):
			return False

		equation = equation.replace('^', '**')

		if eq_type == 'Implicit':
			return self.check_xyz(equation)
		elif eq_type == 'Explicit':
			return self.check_xy(equation)
		elif eq_type == 'Parametric Surface':
			return self.check_uv(equation)
		elif eq_type == "Parametric Curve":
			return self.check_t(equation)
		elif eq_type == 'Vector Field':
			return self.check_xyz(equation)

	def acceptable(self, equation):
		if not equation:
			return False

		if '__' in equation:
			return False

		if '[' in equation or ']' in equation:
			return False

		if '=' in equation:
			return False

		return True

	def check_xyz(self, equation):
		for i in range(5):
			x = random.randint(-100,100)
			y = random.randint(-100,100)
			z = random.randint(-100,100)

			try:
				equation = equation.replace('x', '({0})'.format(str(x)))
				equation = equation.replace('y', '({0})'.format(str(y)))
				equation = equation.replace('z', '({0})'.format(str(z)))
				eval(equation)
			except ZeroDivisionError:
				pass
			except Exception:
				if 'e' in equation and 'p' in equation:
					continue
				return False

		return True

	def check_xy(self, equation):
		for i in range(5):
			x = random.randint(-100,100)
			y = random.randint(-100,100)

			try:
				equation = equation.replace('x', '({0})'.format(str(x)))
				equation = equation.replace('y', '({0})'.format(str(y)))
				eval(equation)
			except ZeroDivisionError:
				pass
			except Exception as e:
				return False

		return True

	def check_uv(self, equation):
		for i in range(5):
			u= random.randint(-100,100)
			v= random.randint(-100,100)

			try:
				equation = equation.replace('u', '({0})'.format(str(u)))
				equation = equation.replace('v', '({0})'.format(str(v)))
				eval(equation)
			except ZeroDivisionError:
				pass
			except Exception as e:
				return False

		return True

	def check_t(self, equation):
		for i in range(5):
			t = random.randint(-100,100)

			try:
				equation = equation.replace('t', '({0})'.format(str(t)))
				eval(equation)
			except ZeroDivisionError:
				pass
			except Exception as e:
				return False

		return True

	def check_bounds(self, expr):
		if not self.acceptable(expr):
			return False

		try:
			eval(expr)
		except:
			return False
		return True