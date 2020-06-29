# Support code for P1

from math import inf
from csv import writer

WALL = 'X'


def load_level(filename):
    """ Loads a level from a given text file.

    Args:
        filename: The name of the txt file containing the maze.

    Returns:
        The loaded level (dict) containing the locations of walls (set), the locations of spaces (dict), and
        a mapping of locations to waypoints (dict).

    """
    walls = set()
    spaces = {}
    waypoints = {}
    with open(filename, "r") as f:

        for j, line in enumerate(f.readlines()):
            for i, char in enumerate(line):
                if char == '\n':
                    continue
                elif char == WALL:
                    walls.add((i, j))
                elif char.isnumeric():
                    spaces[(i, j)] = float(char)
                elif char.islower():
                    spaces[(i, j)] = 1.
                    waypoints[char] = (i, j)

    level = {'walls': walls,
             'spaces': spaces,
             'waypoints': waypoints}

    return level


def show_level(level, path=[]):
    """ Displays a level via a print statement.

    Args:
        level: The level to be displayed.
        path: A continuous path to be displayed over the level, if provided.

    """
    xs, ys = zip(*(list(level['spaces'].keys()) + list(level['walls'])))
    x_lo, x_hi = min(xs), max(xs)
    y_lo, y_hi = min(ys), max(ys)

    path_cells = set(path)

    chars = []
    inverted_waypoints = {point: char for char, point in level['waypoints'].items()}

    for j in range(y_lo, y_hi + 1):
        for i in range(x_lo, x_hi + 1):

            cell = (i, j)
            if cell in path_cells:
                chars.append('*')
            elif cell in level['walls']:
                chars.append('X')
            elif cell in inverted_waypoints:
                chars.append(inverted_waypoints[cell])
            elif cell in level['spaces']:
                chars.append(str(int(level['spaces'][cell])))
            else:
                chars.append(' ')

        chars.append('\n')

    print(''.join(chars))


def save_level_costs(level, costs, filename='distance_map.csv'):
    """ Displays cell costs from an origin point over the given level.

    Args:
        level: The level to be displayed.
        costs: A dictionary containing a mapping of cells to costs from an origin point.
        filename: The name of the csv file to be created.

    """
    xs, ys = zip(*(list(level['spaces'].keys()) + list(level['walls'])))
    x_lo, x_hi = min(xs), max(xs)
    y_lo, y_hi = min(ys), max(ys)

    rows = []
    for j in range(y_lo, y_hi + 1):
        row = []

        for i in range(x_lo, x_hi + 1):
            cell = (i, j)
            if cell not in costs:
                row.append(inf)
            else:
                row.append(costs[cell])

        rows.append(row)

    assert '.csv' in filename, 'Error: filename does not contain file type.'
    with open(filename, 'w', newline='') as f:
        csv_writer = writer(f)
        for row in rows:
            csv_writer.writerow(row)
            
    
    print("Saved file:", filename)