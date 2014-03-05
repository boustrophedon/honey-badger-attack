import pygame


from ecs.System import System

from Components import *

def remove_dead(ent_set):
	dead = set()
	for e in ent_set:
		if e.is_dead:
			dead.add(e)
	ent_set.difference_update(dead)

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

		self.world.globaldata['mapsize'] = (450, 800)

		self.player = self.load_player()
		self.mobs = self.load_mobs()

	def update(self, dt):
		remove_dead(self.mobs)

	def load_player(self):
		""" 1) need to load from a file
			2) need to have an archtype/entity factory thing so that I can just do
			self.player = Player() or something
		"""
		player = self.world.create_entity()
		player.add_component(Type(name="badger"))
		player.add_component(Controllable())
		player.add_component(Position(x=200, y=600))
		player.add_component(MoveSpeed(x=1.5, y=1.5))
		player.add_component(Size(width=25, height=40))
		player.add_component(Color(r=0, g=0, b=0))
		player.add_component(Visible())
		player.add_component(Collidable())

	def load_mobs(self):
		mobs = set()
		m = self.world.create_entity()
		m.add_component(Type(name="mob"))
		m.add_component(Position(x=100, y=100))
		m.add_component(MoveSpeed(x=1, y=1))
		m.add_component(Size(width=20, height=20))
		m.add_component(Color(r=20, g=20, b=20))
		m.add_component(Laser(lastfired=0))
		m.add_component(Visible())
		m.add_component(Hostile())

		mobs.add(m)
		return mobs

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

class CollisionSystem(System):
	""" right now just checks for collision between lasers and badgers """
	def __init__(self, world):
		super(CollisionSystem, self).__init__(world)

		self.world.subscribe_event("ComponentAdded", self)

		self.collidables = self.world.entities_with_components(Collidable) 

		self.badgers = set()

	def receive(self, event_type, event):
		if event_type == "ComponentAdded":
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
		self.screen_size = self.width, self.height = self.world.globaldata['mapsize']
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
	
		remove_dead(self.renderables)	

		self.screen.fill(self.CLEARCOLOR)
		self.render_sprites(dt)
		pygame.display.flip()

#systems = (InputSystem, MovementSystem, RenderSystem)
systems = (InputSystem, MapSystem, AISystem, AttackSystem, LaserSystem, MovementSystem, CollisionSystem, RenderSystem)
