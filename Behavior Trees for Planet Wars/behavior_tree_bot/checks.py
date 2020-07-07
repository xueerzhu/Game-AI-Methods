
def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

# returns true if my weakest planet > 2 * enemy's weakest planet
# instead of repairing internally, attack the weakest enemy planet
# call spread_my_fleet() as a aggressive strategy
def is_stable_enough_to_attack(state):
    weakest_planet = min(state.my_planets(), key=lambda p: p.num_ships, default=None)
    weakest_enemy_planet = min(state.enemy_planets(), key=lambda p: p.num_ships, default=None)
    if weakest_planet and weakest_enemy_planet:
        return weakest_planet.num_ships > weakest_enemy_planet.num_ships * 2
    return False

# returns true if my weakest fleet < half of enemy's strongest feet
# inspire my other fleet to support this planet
# call spread_my_fleet() as a repair strategy
def is_my_weakest_planet_at_risk(state):
    weakest_planet = min(state.my_planets(), key=lambda p: p.num_ships, default=None)
    strongest_enemy_planet = max(state.enemy_planets(), key=lambda p: p.num_ships, default=None)
    if weakest_planet and strongest_enemy_planet:
        return weakest_planet.num_ships < strongest_enemy_planet.num_ships / 2
    return False

# returns true if there is an enemy outpost near a few friendly planet
# initiate attack from the strongest planet among the friendly hub
# call attack_closet_enemy_outpost()
def is_close_enemy_planet(state):
    # Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # sort enemy_planets base on distance from my strongest
    enemy_planets = [planet for planet in state.enemy_planets()
                     if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: state.distance(strongest_planet.ID, p.ID))
    iter_planets = iter(enemy_planets)

    closest_enemy_planet = next(iter_planets)



# returns the neutral planet enemy just attacked
# set it as my immediate attack target to reap the benefit
# call attack_recent_lost_neutral()
def enemy_just_conquered(state):
    # sort enemy_planets
    enemy_planets = [planet for planet in state.enemy_planets()
                     if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: p.num_ships)
    iter_planets = iter(enemy_planets)

    try:
        # if the weakest is < 5, we assume it is a just conquered neutral planet
        weakest_planet = next(iter_planets)
        if weakest_planet:
            return weakest_planet.num_ships < 5
        return False
    except StopIteration:
        return
