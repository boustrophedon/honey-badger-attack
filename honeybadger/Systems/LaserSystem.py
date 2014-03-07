import pygame

from honeybadger.ecs.System import System

from honeybadger.Components import *

from util import remove_dead

class LaserSystem(System):
	def __init__(self, world):
		super(LaserSystem, self).__init__(world)

		self.world.subscribe_event("ComponentAdded", self)
		self.world.subscribe_event("CollisionDetected", self)
		# I should probably filter these closer to the source
		# by passing some parameters, like a filter dict or something 

		self.lasers = set()

	def receive(self, event_type, event):
		if event_type == "ComponentAdded":
			if event.compname == "type" and event.entity.type.name == "laser":
				self.lasers.add(event.entity)
		elif event_type == "CollisionDetected":
			# assume the second entity is the laser
			event.entity2.is_dead = True

	def update(self, dt):
		for laser in self.lasers:
			self.move_laser(laser)
			self.check_out_of_bounds(laser)

		remove_dead(self.lasers)

	def move_laser(self, laser):
		# not sure if i want this to be in the MovementSystem or if that should just be for player and maybe mob movement
		self.world.send_event("MoveEntity", entity=laser, dir=(0,1))

	def check_out_of_bounds(self, laser):
		bounds = self.world.globaldata['mapsize']
		if laser.position.x < 0 or laser.position.x > bounds[0]:
			laser.is_dead = True
		elif 0 > laser.position.y or laser.position.y > bounds[1]:
			laser.is_dead = True
		if laser.is_dead:
			self.world.send_event("EntityDeath", entity=laser)

