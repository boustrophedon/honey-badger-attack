import pygame

from honeybadger.ecs.System import System

from honeybadger.Components import *

from util import remove_dead

class MovementSystem(System):
	def __init__(self, world):
		super(MovementSystem, self).__init__(world)

		self.player = None

		self.world.subscribe_event("ComponentAdded", self)
		self.world.subscribe_event("MovePlayer", self)
		self.world.subscribe_event("MoveEntity", self)

	def receive(self, event_type, event):
		if event_type == "ComponentAdded":
			if event.compname == "controllable":
				self.player = event.entity

		elif event_type == "MovePlayer": 
			self.move_entity(self.player, event.dir)

		elif event_type == "MoveEntity":
			self.move_entity(event.entity, event.dir)
	
	def move_entity(self, e, dir):
		# this needs to be changed probably at the same time as the input system
		# so that we move based on dt. 
		e.position.x += e.movespeed.x * dir[0]
		e.position.y += e.movespeed.y * dir[1]

