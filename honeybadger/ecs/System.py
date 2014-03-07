import World, Entity

class System(object):
	def __init__(self, world):
		self.world = world

	def update(self, dt):
		pass

	def receive(self, event_type, event):
		pass

	def stop(self):
		pass
