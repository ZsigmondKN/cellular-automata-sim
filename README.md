# Bioinspired Assignment

Run on windows
```sh
docker compose up
```

Run on linux
```sh
docker compose -f docker-compose-linux.yml up
```

# TODO
- [x] Populate initial map - Will
- [ ] Buring function - Zig
    - Research + Initial Write-Up (Atal)
    - [DONE] Convection
        - [DONE] Implement different directions
        - [DISCUSSION] Fire spreads too quickly - Now it spreads at a 37km/h
        - [NEW/DONE] The more fire around the higher the chance for the ignite
        - [NEW/DONE] Progressive ignition probability 
        - [DONE] Fire defined on the map burns out by the second frame and as a result sometimes the fire burns out on start.
    - [DONE] Embers
        - [DONE] Implement different directions
    - [DONE] Direct Flame Contact
    - [DONE] Change State (check fuel amount if burning) (chenge fire color based on density, purely performative but nice to have)
    - [DONE] Ensure different materials have different properties
        - [CHECK] Check that the fire still burns for the correct time after finishing all the other todos
- [ ] Regrowth Function - Will
    - Research + Initial Write-Up (Atal)
    - [DONE] Transition
    - Calculate times for regrowth and link back to literature (forest should take months, grass weeks)
- [ ] Map Updates - Week 8 activities
    - [DONE] Add city + fire sources (+size (find a source for this))
    - [DONE] Short Term Invervention
        - Adding wetness (parameters + new state)
    - [DONE] Long Term Intervention
        - Increasing Forest Size
    - [DONE] Remove dependence on temperature

- [ ] Exta stuff (now)
    - [DONE] Remove logo
    - Update colors
    - [DONE] update printLn to state hours that fire reaches town not ticks
    - [DONE] Tune regroth

- [ ] Exta stuff (after we get params from team)
    - Tune fire

- [ ] Once we have date (after results)
    - update long term with proper forest (will - quick)
    - update short term to look like a water drop (will - quick)
    - update long term prescribed burning (will - quick)

# What factors to change
**Default:**
- Power Plant [Wind South]
- Incinerator [Wind South]

**Power Plant & Incinerator:**
- Short Term
- Long Term
- Short + Long Term

**Incinerator:**
- Wind South
- Wind North
- Wind South East