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
        - [TODO] Implement different directions
        - [TODO] Fire spreads too quickly
    - [DONE] Embers
        - [TODO] Implement different directions
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
    - [WJ] Short Term Invervention
        - Adding wetness (parameters + new state)
    - [BUG] Long Term Intervention
        - Increasing Forest Size
    - [DONE] Remove dependence on temperature
    - Update colors

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