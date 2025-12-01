# Bioinspired Assignment running instructions

1, Have Docker and XLaunch running.

2a, For running on windows and Mac, run the following in the main dir:
```sh
docker compose up
```

2b, For running on linux, run the following in the main dir:
```sh
docker compose -f docker-compose-linux.yml up
```

3, When the CAPyLE window launches: \
3.1, Click File \
3.2, Click Open \
3.3, Select "gol_2d_fire.py" \
3.4, Click Open again \
3.5, Maximise the window

4, To run the town fire simulation: \
4.1, select the desired "Grid Setup Option" \
4.2, [optional] change the wind direction from the pre allocated one \
4.3, [optional] you can disable fire ember production
4.4, Click "Apply configuration and run CA"

5, Now you can press "Play" to see the simulation in action.
