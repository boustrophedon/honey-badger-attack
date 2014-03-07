from honeybadger.ecs.World import World

from honeybadger.Systems import systems

if __name__ == '__main__':
	w = World()

	for syst in systems:
		w.register_system(syst)

	w.run()
