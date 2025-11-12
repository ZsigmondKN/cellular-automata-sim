import numpy as np

def generate_multi_region_noise_grid(shape, regions, global_seed=0):
    grid = np.zeros(shape, dtype=int)
    rng_global = np.random.default_rng(global_seed)

    for region in regions:
        x, y = region['x'], region['y']
        w, h = region['width'], region['height']
        min_s, max_s = region['min_state'], region['max_state']

        seed = region.get('seed', rng_global.integers(0, 1e9))
        rng = np.random.default_rng(seed)

        noise = rng.random((h, w))
        values = np.floor(noise * (max_s - min_s + 1)) + min_s
        
        grid[y:y+h, x:x+w] = values.astype(int)
    return grid
