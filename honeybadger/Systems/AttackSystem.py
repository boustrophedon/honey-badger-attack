import pygame

from honeybadger.ecs.System import System

from honeybadger.Components import *

from util import remove_dead

class AttackSystem(System):
	def __init__(self, world):
		super(AttackSystem, self).__init__(world)

		self.hostiles = set()
		self.player = None

		self.world.subscribe_event("MobFireLaser", self)
		self.world.subscribe_event("ComponentAdded", self) # really should add a helper for component adding

	def update(self, dt):
		remove_dead(self.hostiles)

	def receive(self, event_type, event):
		if event_type == "ComponentAdded":
			if event.entity.type.name == "mob":
				self.hostiles.add(event.entity)
			elif event.entity.type.name == "badger":
				self.player = event.entity

		elif event_type == "MobFireLaser":
			if event.mob == None:
				self.fire_all_lasers()
			else:
				self.fire_laser(event.mob)

		elif event_type == "PlayerAttack":
			pass

	def fire_all_lasers(self):
		print("IMMA FIRING MY LASER")
		for mob in self.hostiles:
			self.fire_laser(mob)

	def fire_laser(self, mob):
		center = (mob.position.x+(mob.size.width/2), mob.position.y+(mob.size.height/2))
		self.create_laser(start=center, direction=(0,1)) # in sdl coordinates it is downwards

	def create_laser(self, start, direction, size=(4,18)):
		b = self.world.create_entity()
		b.add_component(Type(name="laser"))
		b.add_component(Size(width=size[0], height=size[1]))
		b.add_component(Position(x=start[0]-(size[0]/2), y=start[1]-(size[1]/2)))
		b.add_component(MoveSpeed(x=direction[0], y=direction[1]))
		b.add_component(Color(r=255, g=0, b=0))
		b.add_component(Visible())
		b.add_component(Collidable())

