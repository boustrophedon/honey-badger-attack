import pygame

from ecs.System import System

from Components import *


class InputSystem(System):
	def __init__(self, world):
		super(InputSystem, self).__init__(world)

		#pygame.key.set_repeat(5,5)
		self.pressed = dict()

		self.lastup = dict() #doubletap detection

		self.world.subscribe_event('KeyDown', self)
		self.world.subscribe_event('KeyUp', self)

	def update(self, dt):
		# I think this essentially does pygame.key.set_repeat
		# rather than sending the keydown i should "do the thing inside the corresponding if statement" for that key
		# so i can distinguish between physically pressing the key and having it be pressed
		for key in self.pressed.keys(): #haha keys
			self.press_key('KeyDown', key)

	def press_key(self, press_type, key):
		# should really just have a keyhandlers.py and then hook the functions in
		# maybe using python magic to do it automatically
		# or a KeyHandler class with an instance for KeyDown and KeyUp?
		if press_type == 'KeyDown':
			self.pressed[key] = True

			if (key == pygame.K_ESCAPE):
				#self.world.send_event("Quit")
				self.world.stop = True # above would probably be better, but I don't know where to handle it

			elif (key == pygame.K_UP):
				if (pygame.time.get_ticks() - self.lastup.get(key, -100) < 100):
					self.world.send_event("PlayerAttack")
					self.lastup.pop(key)
				else:
					self.world.send_event("MovePlayer", dir="Up")

			elif (key == pygame.K_DOWN):
				self.world.send_event("MovePlayer", dir="Down")
			elif (key == pygame.K_LEFT):
				self.world.send_event("MovePlayer", dir="Left")
			elif (key == pygame.K_RIGHT):
				self.world.send_event("MovePlayer", dir="Right")

			elif (key == pygame.K_y):
				print(self.world.clock.get_fps())

		if (press_type == 'KeyUp'):
			if self.pressed.get(key, False):
				self.pressed.pop(key)
			self.lastup[key] = pygame.time.get_ticks() 

	def receive(self, event_type, event):
		self.press_key(event_type, event.key)

class MapSystem(System):
	""" not really sure if this is a good idea. handles loading the map?
		i.e. puts the player on the board, and spawns enemies
		I guess I'm not sure about like,
		if I had static terrain or wanted to use a grid system for collision detection
		where would that data go? and who would handle it?
		I suppose that what would happen is:
		- the input system would create a move event
		- next tick it would go to the movement system
		- next tick? the collision system would notice we moved into a solid object?
		or should the movement system realize we can't do that

		as someone said on SO: I have a new hammer and now everything looks like a nail
		maybe try "spaces" i.e. multiple state-holding world objects
		http://gamedev.stackexchange.com/questions/60907/how-would-one-store-global-context-data-in-an-entity-component-system
	"""

	def __init__(self, world):
		super(MapSystem, self).__init__(world)

		self.load_player()
		self.load_mobs()

	def load_player(self):
		""" 1) need to load from a file
			2) need to have an archtype/entity factory thing so that I can just do
			self.player = Player() or something
		"""
		self.player = self.world.create_entity()
		self.player.add_component(Controllable())
		self.player.add_component(Position(x=100, y=100))
		self.player.add_component(Size(width=25, height=40))
		self.player.add_component(Color(r=0, g=0, b=0))
		self.player.add_component(Visible())

	def load_mobs(self):
		print("stubbed")

class MovementSystem(System):
	def __init__(self, world):
		super(MovementSystem, self).__init__(world)

		self.player = None

		self.world.subscribe_event("ComponentAdded", self)
		self.world.subscribe_event("MovePlayer", self)

	def receive(self, event_type, event):
		if event_type == "ComponentAdded":
			if event.compname == "controllable":
				self.player = event.entity

		elif event_type == "MovePlayer": 
			self.move_player(event.dir)
	
	def move_player(self, dir):
		if dir == "Up":
			self.player.position.y -= 1.5
		elif dir == "Down":
			self.player.position.y += 1.5
		elif dir == "Left":
			self.player.position.x -= 1.5
		elif dir == "Right":
			self.player.position.x += 1.5

class RenderSystem(System):
	CLEARCOLOR = (237, 201, 175) # "desert sand"

	def __init__(self, world):
		super(RenderSystem, self).__init__(world)

		self.init_pygame()

		self.update_renderables()

		self.world.subscribe_event("ComponentAdded", self)

	def receive(self, event_type, event):
		if event_type == "ComponentAdded" and event.compname == "visible":
			e = event.entity
			if e.has_components(Position, Size, Color):
				self.create_sprite(e)
				self.update_renderables()
			if e.has_component(Controllable):
				# then we are a motherfucking honey badger
				# add stripes
				e.pygamesurf.surface.fill((255,255,255), ((3, 0), (e.size.width-6, e.size.height)))
				e.pygamesurf.surface.fill((128, 128, 128), ((6, 0), (e.size.width-12, e.size.height)))

				# add eyes
				e.pygamesurf.surface.fill((255,0,0), ((6, 5), (3,3)))
				e.pygamesurf.surface.fill((255,0,0), ((16, 5), (3,3)))


	def update_renderables(self):
		self.renderables = self.world.entities_with_components(Position, Size, Color, Visible, PygameSurf)

	def init_pygame(self):
		self.screen_size = self.width, self.height = 450, 800 # need some sort of options system or something? I guess really I should read from a config file
		self.screen = pygame.display.set_mode(self.screen_size)

	def create_sprite(self, entity):
		surf = pygame.Surface((entity.size.width, entity.size.height))
		surf.fill((entity.color.r, entity.color.g, entity.color.b))
		surf.convert(self.screen)
		entity.add_component(PygameSurf(surface=surf))

	def render_sprites(self, dt):
		for sprite in self.renderables:
			self.screen.blit(sprite.pygamesurf.surface, (sprite.position.x, sprite.position.y))

	def update(self, dt):
		#rather than doing this each frame, I should do it when an entity is created or something

		self.screen.fill(self.CLEARCOLOR)
		self.render_sprites(dt)
		pygame.display.flip()

#systems = (InputSystem, MovementSystem, RenderSystem)
systems = (InputSystem, MapSystem, MovementSystem, RenderSystem)
