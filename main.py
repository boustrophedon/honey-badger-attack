from ecs.World import World
from ecs.Entity import Entity
from ecs.Component import ComponentFactory as Comp

from Systems import *

if __name__ == '__main__':
	w = World()

	for syst in systems:
		w.register_system(syst)

	w.run()
