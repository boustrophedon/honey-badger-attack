import pygame

from honeybadger.ecs.System import System

from honeybadger.Components import *

from syst_util import remove_dead

class CollisionSystem(System):
	""" right now just checks for collision between lasers and badgers """
	def __init__(self, world):
		super(CollisionSystem, self).__init__(world)

		self.world.subscribe_event("ComponentAdded", self.onComponentAdded)

		self.collidables = self.world.entities_with_components(Collidable) 

		self.badgers = set()

	def onComponentAdded(self, event_type, event):
		if event.entity.type.name == "badger":
			self.badgers.add(event.entity)
		if event.compname == "collidable":
			# non-badger collidables, should really check typename lasers
			self.collidables.add(event.entity)

	def update(self, dt):
		for b in self.badgers:
			for e in self.collidables-self.badgers:
				if self.check_collision(b, e):
					self.world.send_event("CollisionDetected", entity1=b, entity2=e)

		remove_dead(self.collidables)

	def check_collision(self, b, e):
		""" should abstract out the bounding box or something.
			it is sufficiently abstracted now so that changes only affect this function though
		"""
		r1 = pygame.Rect(b.position.x, b.position.y, b.size.width, b.size.height)
		r2 = pygame.Rect(e.position.x, e.position.y, e.size.width, e.size.height)
		return r1.colliderect(r2)

