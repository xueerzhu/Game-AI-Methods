#!/usr/bin/env python
#

from math import ceil, sqrt
from collections import namedtuple
from sys import stdout
import logging


def issue_order(state, source_planet_ID, destination_planet_ID, fleet_num_ships):
    # Check for legal order
    planet = state.planets[source_planet_ID]
    if planet.num_ships < fleet_num_ships or planet.owner != 1:
        logging.debug("Bad order:" + ' '.join([str(source_planet_ID), str(planet.num_ships), str(fleet_num_ships)]))
        return False

    # Update state
    distance = state.distance(source_planet_ID, destination_planet_ID)
    state.fleets.append(Fleet(1, fleet_num_ships, source_planet_ID, destination_planet_ID, distance, distance))
    state.planets[source_planet_ID] = planet._replace(num_ships =planet.num_ships - fleet_num_ships)

    # Send order
    logging.debug("Order:" + ' '.join([str(source_planet_ID), str(destination_planet_ID), str(fleet_num_ships)]))
    stdout.write("%d %d %d\n" % (source_planet_ID, destination_planet_ID, fleet_num_ships))
    stdout.flush()
    return True


def finish_turn():
    # Must pass "go" to game.
    logging.debug('Finish turn\n')
    stdout.write("go\n")
    stdout.flush()


Fleet = namedtuple('Fleet', ['owner', 'num_ships', 'source_planet', 'destination_planet', 'total_trip_length',
                             'turns_remaining'])

Planet = namedtuple('Planet', ['ID', 'x', 'y', 'owner', 'num_ships', 'growth_rate'])


class PlanetWars:
    def __init__(self, game_state):
        self.planets = []
        self.fleets = []
        parse_game_state(self, game_state)

    def my_planets(self):
        return [planet for planet in self.planets if planet.owner == 1]

    def neutral_planets(self):
        return [planet for planet in self.planets if planet.owner == 0]

    def enemy_planets(self):
        return [planet for planet in self.planets if planet.owner == 2]

    def not_my_planets(self):
        return [planet for planet in self.planets if planet.owner != 1]

    def my_fleets(self):
        return [fleet for fleet in self.fleets if fleet.owner == 1]

    def enemy_fleets(self):
        return [fleet for fleet in self.fleets if fleet.owner == 2]

    def __str__(self):
        s = ''
        for p in self.planets:
            s += "P %f %f %d %d %d\n" % \
                 (p.x(), p.y(), p.owner, p.num_ships(), p.growth_rate())
        for f in self.fleets:
            s += "F %d %d %d %d %d %d\n" % \
                 (f.owner, f.num_ships(), f.source_planet(), f.destination_planet(),
                  f.total_trip_length(), f.turns_remaining())
        return s

    def distance(self, source_planet, destination_planet):
        source = self.planets[source_planet]
        destination = self.planets[destination_planet]
        dx = source.x - destination.x
        dy = source.y - destination.y
        return int(ceil(sqrt(dx * dx + dy * dy)))

    def is_alive(self, player_id):
        return any(planet.owner == player_id for planet in self.planets) or \
                any(fleet.owner == player_id for fleet in self.fleets)


def parse_game_state(pw_instance, state):
    lines = state.split("\n")

    planet_lines = [line for line in lines if line.startswith('P')]
    fleet_lines = [line for line in lines if line.startswith('F')]

    for planet_id, line in enumerate(planet_lines):
        line = line.split('#')[0]
        params = line.split(' ')[1:]
        assert len(params) == 5, 'Wrong planet specification: ' + line

        p = Planet(planet_id, *map(float, params))
        pw_instance.planets.append(p)

    for line in fleet_lines:
        line = line.split('#')[0]
        params = line.split(' ')[1:]
        assert len(params) == 6, 'Wrong fleet specification: ' + line

        f = Fleet(*map(int, params))
        pw_instance.fleets.append(f)
