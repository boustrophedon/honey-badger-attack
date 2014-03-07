import pygame

from honeybadger.ecs.System import System

from honeybadger.Components import *

from util import remove_dead

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

