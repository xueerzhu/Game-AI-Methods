import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    neutral_planets = [planet for planet in state.neutral_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    # neutral_planets.sort(key=lambda p: p.num_ships)
    neutral_planets.sort(key=lambda p: p.num_ships + state.distance(strongest_planet.ID, p.ID))

    target_planets = iter(neutral_planets)

    try:
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + 1

            if strongest_planet.num_ships > required_ships:
                issue_order(state, strongest_planet.ID, target_planet.ID, required_ships)
                target_planet = next(target_planets)
            else:
                return False

    except StopIteration:
        return

def attack_closet_enemy_outpost(state):
    # Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # sort enemy_planets base on distance from my strongest
    enemy_planets = [planet for planet in state.enemy_planets()
                     if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: state.distance(strongest_planet.ID, p.ID))
    iter_planets = iter(enemy_planets)

    try:
        closest_enemy_planet = next(iter_planets)

        # attack
        if not strongest_planet or not closest_enemy_planet:
            return False
        else:
            required_ships = closest_enemy_planet.num_ships + \
                             state.distance(strongest_planet.ID, closest_enemy_planet.ID) * closest_enemy_planet.growth_rate + 1

            if strongest_planet.num_ships > required_ships:
                return issue_order(state, strongest_planet.ID, closest_enemy_planet.ID, required_ships + 20)
            else:
                return False
    except StopIteration:
        return

def spread_my_fleet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) If our largest planet is not at least three times our weakest planet, we abort spread
    if min(planet.num_ships for planet in state.my_planets()) > max(planet.num_ships for planet in state.my_planets()) / 3:
        return False

    # (3) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (4) Find my weakest planet.
    weakest_planet = min(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (4) Send a third of the ships from my strongest planet to my weakest planet.
    return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 3)

def attack_recent_lost_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Get target enemy planet
    enemy_planets = [planet for planet in state.enemy_planets()
                     if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: p.num_ships)
    iter_planets = iter(enemy_planets)

    # (3) Get my planet iter
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    # (4) Calculate the least amount of ships we need to send
    try:
        my_planet = next(my_planets)
        target_planet = next(iter_planets)
        while True:
            required_ships = target_planet.num_ships + \
                                 state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships + 20)
                my_planet = next(my_planets)
                target_planet = next(iter_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return


