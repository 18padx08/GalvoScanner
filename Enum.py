import re
class Enum(object):
	def __init__(self, *args, **kwargs):
		#loop through args and asign values according to enum rules
		self._enumvals = {}
		m = re.compile("[A-z,\s]*\=\s*\d*")
		countingVar = 0
		for arg in args:
			if m.match(arg) is not None:
				mat = m.match(arg).group().split("=")
				super(Enum, self).__getattribute__("_enumvals")[mat[0].strip()] = mat[1].strip()
				countingVar = int(mat[1].strip()) + 1
			else:
				super(Enum,self).__getattribute__("_enumvals")[arg.strip()] = countingVar
				countingVar += 1
	
	def __getattribute__(self, attr):
		return super(Enum, self).__getattribute__("_enumvals")[attr]

	def __setattr__(self, attr, val):
		if attr == "_enumvals":
			super(Enum, self).__setattr__("_enumvals",  val)
		else:
			super(Enum, self).__getattribute__("_enumvals")[attr] = val
	def __call__(self, integer):
		if type(integer) is str:
			return super(Enum, self).__getattribute__("_enumvals")[integer]
		a = super(Enum, self).__getattribute__("_enumvals")
		for key in a:
			if a[key] == integer:
				return key
		return None	