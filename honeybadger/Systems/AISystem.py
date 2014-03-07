import pygame

from honeybadger.ecs.System import System

from honeybadger.Components import *

from util import remove_dead

class AISystem(System):
	def __init__(self, world):
		super(AISystem, self).__init__(world)

		self.player = None
		
		self.update_hostiles()

		self.world.subscribe_event("ComponentAdded", self)

	def receive(self, event_type, event):
		if event_type == "ComponentAdded":
			if event.entity.type.name == 'badger':
				self.player = event.entity

	def update(self, dt):
		self.update_hostiles()

		if self.player:
			self.move_hostiles_towards_player()
			self.fire_if_in_range()

		remove_dead(self.hostiles)

	def move_hostiles_towards_player(self):
		for mob in self.hostiles:
			self.move_towards_player(mob)

	def move_towards_player(self, mob):
		if self.player.position.x < mob.position.x:
			self.world.send_event("MoveEntity", entity=mob, dir=(-1,0))
		elif self.player.position.x > mob.position.x:
			self.world.send_event("MoveEntity", entity=mob, dir=(1,0))

	def fire_if_in_range(self):
		for mob in self.hostiles:
			if self.in_range(mob, self.player):
				self.fire_laser(mob)

	def in_range(self, mob, badger):
		if abs(badger.position.x - mob.position.x) < 10:
			self.fire_laser(mob)
			
	def fire_laser(self, mob):
		if ((pygame.time.get_ticks() - mob.laser.lastfired) > 500) :
			self.world.send_event("MobFireLaser", mob=mob)
			mob.laser.lastfired = pygame.time.get_ticks()

	def update_hostiles(self):
		self.hostiles = self.world.entities_with_components(Hostile)

