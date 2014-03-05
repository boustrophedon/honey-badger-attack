from pygame import Surface

from ecs.Component import ComponentFactory

# these should really be loaded from eg a json file or something
# first load the component definitions, then load saved component data

Type = ComponentFactory("type", ("name",))

Position = ComponentFactory("position", ("x", "y"))
Velocity = ComponentFactory("velocity", ("x", "y"))
Color = ComponentFactory("color", ("r","g","b"))
Size = ComponentFactory("size", ("height", "width"))
Visible = ComponentFactory("visible", tuple())

PygameSurf = ComponentFactory("pygamesurf", ("surface",))

Controllable = ComponentFactory("controllable", tuple())

Collidable = ComponentFactory("collidable", tuple())

Hostile = ComponentFactory("hostile", tuple())

