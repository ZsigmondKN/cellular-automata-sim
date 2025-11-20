def get_additional_funcs():
    return [("Fire at Incinerator", setFireIncinerator), 
            ("Fire at Power Plant", setFireFactory),
            ("Custom Edit", do_nothing)]

def setFireIncinerator(config):
    set_square(config, origin=(0, 198), size=2)

def setFireFactory(config):
    set_square(config, origin=(0, 20), size=2)

def do_nothing(config):
    pass

def set_square(config, origin, size):
    config.initfire = []
    ox, oy = origin

    coords = []
    for dx in range(size):
        for dy in range(size):
            coords.append((ox + dy, oy + dx))

    config.initfire = coords

def get_additional_wind_dir(config):
    directions = [
        "No Wind", "N to S", "NE to SW", "E to W",
        "SE to NW", "S to N", "SW to NE", "W to E", "NW to SE"
    ]
    return [(name, make_wind_setter(name)) for name in directions]


def make_wind_setter(direction_name):
    def setter(config):
        config.wind_direction_set = direction_name
    return setter

def get_additional_ember_set(config):
    return [
        ("Enable Embers", lambda c=config: set_enable_embers(c)),
        ("Disable Embers", lambda c=config: set_disable_embers(c))
    ]

def set_enable_embers(config):
    config.ember_set = True

def set_disable_embers(config):
    config.ember_set = False