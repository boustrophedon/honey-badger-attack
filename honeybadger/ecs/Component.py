from Record import recordtype

class ComponentFactory(object):
	def __init__(self, name, attrs):
		self.name = name
		self.comp = recordtype(name, ('COMPNAME',)+attrs)

	def __call__(self, **kwargs):
		if 'COMPNAME' in kwargs:
			raise ValueError("Component data shouldn't specify a COMPNAME key.")

		kwargs['COMPNAME'] = self.name
		return self.comp(**kwargs)

