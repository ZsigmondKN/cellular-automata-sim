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


def integer_points_on_circle(cx, cy, r):
    points = []
    r2 = r * r

    for x in range(cx - r, cx + r + 1):
        dx2 = (x - cx) ** 2
        dy2 = r2 - dx2

        if dy2 < 0:
            continue

        y_root = dy2 ** 0.5

        for y_real in (cy + y_root, cy - y_root):
            y = round(y_real)

            if abs((x - cx)**2 + (y - cy)**2) <= r2:
                points.append((x, y))

    points = list(set(points))
    points.sort()
    return points