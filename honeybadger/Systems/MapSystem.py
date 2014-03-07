import pygame

from honeybadger.ecs.System import System

from honeybadger.Components import *

from syst_util import remove_dead

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

