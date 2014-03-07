import pygame

from honeybadger.ecs.System import System

from honeybadger.Components import *

from syst_util import remove_dead

class MovementSystem(System):
	def __init__(self, world):
		super(MovementSystem, self).__init__(world)

		self.player = None

		self.world.subscribe_event("ComponentAdded", self.onComponentAdded)
		self.world.subscribe_event("MovePlayer", self.onMovePlayer)
		self.world.subscribe_event("MoveEntity", self.onMoveEntity)

	def onComponentAdded(self, event_type, event):
		if event.compname == "controllable":
			self.player = event.entity

	def onMovePlayer(self, event_type, event):
		self.move_entity(self.player, event.dir)

	def onMoveEntity(self, event_type, event):
		self.move_entity(event.entity, event.dir)
	
	def move_entity(self, e, dir):
		# this needs to be changed probably at the same time as the input system
		# so that we move based on dt. 
		e.position.x += e.movespeed.x * dir[0]
		e.position.y += e.movespeed.y * dir[1]

