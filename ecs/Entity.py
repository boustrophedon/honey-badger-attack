import World

class Entity(object):
	def __init__(self, world):
		self.world = world
		self.components = dict()

		self.is_dead = False

	def add_component(self, comp):
		self.components[comp.COMPNAME] = comp
		self.world.register_component(self, comp)

	def has_component(self, comp_type):
		if self.components.get(comp_type.name, False):
			return True
		else:
			return False

	def has_components(self, *comp_types):
		if all(self.has_component(t) for t in comp_types):
			return True
		else:
			return False

	def __getattr__(self, attr):
		try:
			return self.components[attr]
		except KeyError, err:
			raise AttributeError("Entity has no attribute " + attr)

