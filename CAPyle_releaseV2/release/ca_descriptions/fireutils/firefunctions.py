def get_additional_funcs():
    return [("Set fire incinerator", setFireIncinerator), ("Set fire Power Plant", setFireFactory)]

def setFireIncinerator(config):
    set_square(config, origin=(0, 196), size=2)

def setFireFactory(config):
    set_square(config, origin=(0, 20), size=2)

def set_square(config, origin, size):
    config.initfire = []
    ox, oy = origin

    coords = []
    for dx in range(size):
        for dy in range(size):
            coords.append((ox + dy, oy + dx))

    config.initfire = coords