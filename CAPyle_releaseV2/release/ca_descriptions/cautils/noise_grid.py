import numpy as np

def generate_multi_region_noise_grid(shape, regions, global_seed=0):
    """
    Generate a grid subdivided into regions, each with its own seeded noise and value range.

    Parameters
    ----------
    shape : tuple
        Overall grid shape (rows, cols)
    regions : list of dict
        Each dict defines a rectangle with:
            {
                'x': start column,
                'y': start row,
                'width': width in cells,
                'height': height in cells,
                'min_state': int,
                'max_state': int,
                'seed': int (optional)
            }
    global_seed : int
        Base seed used if individual regions don't specify one.

    Returns
    -------
    np.ndarray
        Integer grid with combined region noise.
    """
    grid = np.zeros(shape, dtype=int)
    rng_global = np.random.default_rng(global_seed)

    for region in regions:
        # Extract region parameters
        x, y = region['x'], region['y']
        w, h = region['width'], region['height']
        min_s, max_s = region['min_state'], region['max_state']

        # Generate sub-grid noise
        seed = region.get('seed', rng_global.integers(0, 1e9))
        rng = np.random.default_rng(seed)

        noise = rng.random((h, w))
        values = np.floor(noise * (max_s - min_s + 1)) + min_s

        # Insert into main grid
        grid[y:y+h, x:x+w] = values.astype(int)

    return grid