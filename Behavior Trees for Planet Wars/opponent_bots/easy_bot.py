#!/usr/bin/env python
#
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from planet_wars import PlanetWars, issue_order, finish_turn


def do_turn(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest enemy or neutral planet.
    weakest_planet = min(state.not_my_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return

    # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
    issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships/2)


if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)

    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
