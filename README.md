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
    - [TODO] Embers
        - [TODO] Implement different directions
    - [DONE] Direct Flame Contact
    - [DONE] Change State (check fuel amount if burning) (chenge fire color based on density, purely performative but nice to have)
    - [DONE] Ensure different materials have different properties
- [ ] Regrowth Function - Will
    - Research + Initial Write-Up (Atal)
    - Transition
- [ ] Map Updates - Week 8 activities
    - Add city + fire sources (+size (find a source for this))
    - Short Term Invervention
        - Adding wetness (parameters + new state)
    - Long Term Intervention
        - Increasing Forest Size
    - Remove dependence on temperature
    
