import pygame

from honeybadger.ecs.System import System

from honeybadger.Components import *

from syst_util import remove_dead

class InputSystem(System):
	def __init__(self, world):
		super(InputSystem, self).__init__(world)

		#pygame.key.set_repeat(5,5)
		self.pressed = dict()

		self.lastup = dict() #doubletap detection

		self.world.subscribe_event('KeyDown', self.onKeyDown)
		self.world.subscribe_event('KeyUp', self.onKeyUp)

	def update(self, dt):
		# I think this essentially does pygame.key.set_repeat
		# rather than sending the keydown i should "do the thing inside the corresponding if statement" for that key
		# so i can distinguish between physically pressing the key and having it be pressed
		for key in self.pressed.keys(): #haha keys
			self.press_key(key)

	def press_key(self, key):
		# should really just have a keyhandlers.py and then hook the functions in
		# maybe using python magic to do it automatically
		# or a KeyHandler class with an instance for KeyDown and KeyUp?
		# some time after above: i think i still need a ControlScheme class or something to map between keys and what they do
		# essentially a dict that has callbacks for various keypresses
		# actually two dicts:
		# one "function description (eg 'jump') --> key" for remapping purposes
		# two "key --> callback"
		self.pressed[key] = True

		if (key == pygame.K_ESCAPE):
			#self.world.send_event("Quit")
			self.world.stop = True # above would probably be better, but I don't know where to handle it

		elif (key == pygame.K_UP):
			if (pygame.time.get_ticks() - self.lastup.get(key, -100) < 100):
				self.world.send_event("PlayerAttack")
				self.lastup.pop(key)
			else:
				self.world.send_event("MovePlayer", dir=(0,-1))

		elif (key == pygame.K_DOWN):
			self.world.send_event("MovePlayer", dir=(0,1))
		elif (key == pygame.K_LEFT):
			self.world.send_event("MovePlayer", dir=(-1,0))
		elif (key == pygame.K_RIGHT):
			self.world.send_event("MovePlayer", dir=(1,0))

		elif (key == pygame.K_SPACE):
			self.world.send_event("MobFireLaser", mob=None)
			self.pressed.pop(key)

		elif (key == pygame.K_y):
			print(self.world.clock.get_fps())
			self.pressed.pop(key)

	def lift_key(self, key):
		if self.pressed.get(key, False):
			self.pressed.pop(key)
		self.lastup[key] = pygame.time.get_ticks() 

	def onKeyDown(self, event_type, event):
		self.press_key(event.key)

	def onKeyUp(self, event_type, event):
		self.lift_key(event.key)

