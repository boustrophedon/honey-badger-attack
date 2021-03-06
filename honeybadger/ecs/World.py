import pygame

from collections import defaultdict

from Entity import Entity

def check_event_matches(event, matches):
	""" I don't really know why I felt this shouldn't be a class method of world
		but it feels like it shouldn't.
		I also feel like there should be a much more pythonic way to do this
		or at least using like filter() or something
	"""
	if matches is None:
		return True
	for k,v in matches.items():
		if not (hasattr(event, k) and getattr(event,k) == v):
			return False
	return True

class World(object):
	def __init__(self):
		pygame.init()

		self.entities = list()
		self.components = defaultdict(set)
		self.systems = list()

		self.globaldata = dict() # i don't really like this but I don't see a better way

		self.event_subs = defaultdict(list)

		self.clock = pygame.time.Clock()

		self.stop = False

	def create_entity(self):
		e = Entity(self)
		self.entities.append(e)

		return e

	def register_component(self, e, comp):
		self.components[comp.COMPNAME].add(e)
		self.send_event("ComponentAdded", compname=comp.COMPNAME, entity=e)

	def entities_with_components(self, *comp_types):
		ents = [self.components[c.name] for c in comp_types]
		if len(ents) == 1:
			return ents[0]
		else:
			return ents[0].intersection(*ents[1:])

	def register_system(self, syst):
		self.systems.append(syst(self))

	def update_systems(self, dt):
		for syst in self.systems:
			syst.update(dt) # should maybe add a tickrate to the systems
							# alt, give each system its own clock then can call clock.tick(sysfps)

	def subscribe_event(self, event_type, event_callback, matches=None):
		self.event_subs[event_type].append((event_callback, matches))

	def send_event(self, event_type, **kwargs):
		pygame.event.post(pygame.event.Event(pygame.USEREVENT, typename=event_type, **kwargs))

	def process_event(self, event):
		event_type = pygame.event.event_name(event.type)
		if event_type == 'UserEvent':
			event_type = event.typename

		for callback,matches in self.event_subs[event_type]:
			if check_event_matches(event, matches):
				callback(event_type, event)

	def process_events(self):
		for event in pygame.event.get():
			self.process_event(event)

	def run(self):
		while not self.stop:
			self.update_systems(self.clock.tick(120))
			self.process_events()
		self.shutdown()

	def shutdown(self):
		for syst in self.systems:
			syst.stop()
