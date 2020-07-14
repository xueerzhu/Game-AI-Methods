import pathfinding
import numpy as np
import sys


def metrics(levelStr):
    maxY = len(levelStr)
    maxX = len(levelStr[0])

    visited = set()
    curX = 2
    curY = 0
    solids = set(['X', 'Q', 'S', '?', 'B', 'b', '[', ']', 'T', '|', '<', '>', 'v', 'f', 'm'])

    def isSolid(tile):
        return tile in solids
    for yy in range(maxY - 2, -1, -1):
        if (levelStr[yy][curX] == '-' or levelStr[yy][curX] == '*') and isSolid(levelStr[yy + 1][curX]):
            curY = yy
            break

    jumps = [[(0, -1),
              (0, -2),
              (1, -3),
              (1, -4),
              (0, -4)],
             [(0, -1),
              (0, -2),
              (0, -3),
              (0, -4),
              (1, -4)],
             [(1, -1),
              (1, -2),
              (1, -3),
              (1, -4),
              (2, -4)],
             [(1, -1),
              (1, -2),
              (2, -2),
              (2, -3),
              (3, -3),
              (3, -4),
              (4, -4),
              (5, -3),
              (6, -3),
              (7, -3),
              (8, -2),
              (8, -1)],
             [(1, -1),
              (1, -2),
              (2, -2),
              (2, -3),
              (3, -3),
              (3, -4),
              (4, -4),
              (5, -4),
              (6, -3),
              (7, -3),
              (8, -2),
              (8, -1)]]
    jumpDiffs = []
    for jump in jumps:
        jumpDiff = [jump[0]]
        for ii in range(1, len(jump)):
            jumpDiff.append((jump[ii][0] - jump[ii - 1][0], jump[ii][1] - jump[ii - 1][1]))
        jumpDiffs.append(jumpDiff)
    jumps = jumpDiffs
    visited = set()

    def getNeighbors(pos):
        dist = pos[0]
        pos = pos[1]
        visited.add((pos[0], pos[1]))
        below = (pos[0], pos[1] + 1)
        neighbors = []
        if below[1] >= maxY:
            return []
        if pos[2] != -1:
            ii = pos[3] + 1
            jump = pos[2]
            if ii < len(jumps[jump]):
                if not (pos[0] + pos[4] * jumps[jump][ii][0] >= maxX or pos[0] + pos[4] * jumps[jump][ii][0] < 0 or pos[1] + jumps[jump][ii][1] < 0) and not isSolid(levelStr[pos[1] + jumps[jump][ii][1]][pos[0] + pos[4] * jumps[jump][ii][0]]):
                    neighbors.append([dist + 1, (pos[0] + pos[4] * jumps[jump][ii][0], pos[1] + jumps[jump][ii][1], jump, ii, pos[4])])

        if isSolid(levelStr[below[1]][below[0]]):
            if pos[0] + 1 < maxX and not isSolid(levelStr[pos[1]][pos[0] + 1]):
                neighbors.append([dist + 1, (pos[0] + 1, pos[1], -1)])
            if pos[0] - 1 >= 0 and not isSolid(levelStr[pos[1]][pos[0] - 1]):
                neighbors.append([dist + 1, (pos[0] - 1, pos[1], -1)])

            for jump in range(len(jumps)):
                ii = 0
                if not (pos[0] + jumps[jump][ii][0] >= maxX or pos[1] + jumps[jump][ii][1] < 0) and not isSolid(levelStr[pos[1] + jumps[jump][ii][1]][pos[0] + jumps[jump][ii][0]]):
                    neighbors.append([dist + ii + 1, (pos[0] + jumps[jump][ii][0], pos[1] + jumps[jump][ii][1], jump, ii, 1)])

                if not (pos[0] - jumps[jump][ii][0] < 0 or pos[1] + jumps[jump][ii][1] < 0) and not isSolid(levelStr[pos[1] + jumps[jump][ii][1]][pos[0] - jumps[jump][ii][0]]):
                    neighbors.append([dist + ii + 1, (pos[0] - jumps[jump][ii][0], pos[1] + jumps[jump][ii][1], jump, ii, -1)])

        else:
            neighbors.append([dist + 1, (pos[0], pos[1] + 1, -1)])
            if pos[1] + 1 < maxY:
                if pos[0] + 1 < maxX and not isSolid(levelStr[pos[1] + 1][pos[0] + 1]):
                    neighbors.append([dist + 1.4, (pos[0] + 1, pos[1] + 1, -1)])
                if pos[0] - 1 >= 0 and not isSolid(levelStr[pos[1] + 1][pos[0] - 1]):
                    neighbors.append([dist + 1.4, (pos[0] - 1, pos[1] + 1, -1)])
            if pos[1] + 2 < maxY:
                if pos[0] + 1 < maxX and not isSolid(levelStr[pos[1] + 2][pos[0] + 1]):
                    neighbors.append([dist + 2, (pos[0] + 1, pos[1] + 2, -1)])
                if pos[0] - 1 >= 0 and not isSolid(levelStr[pos[1] + 2][pos[0] - 1]):
                    neighbors.append([dist + 2, (pos[0] - 1, pos[1] + 2, -1)])
        return neighbors
    subOptimal = 0

    paths = pathfinding.dijkstras_shortest_path((curX, curY, -1), lambda pos: pos[0] == maxX - 2, getNeighbors, subOptimal)

    pathDict = {path[0]: [] for path in paths}

    for yy in range(maxY):
        s = ''
        for xx in range(maxX):
            if (xx, yy) in visited:
                s += '*'
            else:
                s += levelStr[yy][xx]

        # print s
    for path in paths:
        pathDict[path[0]].append([(p[0], p[1]) for p in path[1]])
    # print paths
    paths = pathDict
    pathStats = {}
    gaps = set()
    for xx in range(maxX):
        if levelStr[maxY - 1][xx] == '-':
            gaps.add(xx)
    for pathLength in paths:
        pathStats[pathLength] = {'jumps': [], 'meaningfulJumps': []}
        for path in paths[pathLength]:
            jumps = 0
            meaningfulJumps = 0
            onGround = True
            for p in path:
                if p[1] < 15 and isSolid(levelStr[p[1] + 1][p[0]]):
                    onGround = True
                elif onGround:
                    jumps += 1
                    onGround = False
                    for xx in range(5):
                        if p[0] + xx < maxX and p[0] + xx in gaps:
                            meaningfulJumps += 1
                            break
            pathStats[pathLength]['jumps'].append(jumps)
            pathStats[pathLength]['meaningfulJumps'].append(meaningfulJumps)
    totalJumps = 0
    totalMeaningfulJumps = 0
    pathcount = 0
    smallest = float('inf')

    for path in pathStats:
        if path < smallest:
            smallest = path
        for p in pathStats[path]['jumps']:
            totalJumps += p
            pathcount += 1
        for p in pathStats[path]['meaningfulJumps']:
            totalMeaningfulJumps += p
    jumpVariance = 0
    meaningfulJumpVariance = 0

    for path in pathStats:
        for p in pathStats[path]['jumps']:
            temp = p - float(totalJumps) / float(pathcount)
            jumpVariance += temp * temp

        for p in pathStats[path]['meaningfulJumps']:
            temp = p - float(totalMeaningfulJumps) / float(pathcount)
            meaningfulJumpVariance += temp * temp

    totalSize = maxX * maxY
    #negativeSpace = float(len(visited))/float(totalSize)
    enemies = 0
    pipes = 0
    empty = 0
    breakable = 0
    rewards = 0
    solid = 0
    powerups = 0
    for row in levelStr:
        enemies += row.count('E')
        empty += row.count('-') + row.count('E') + row.count('o') + row.count('*')
        pipes += row.count('|') + row.count('T')
        breakable += row.count('B')
        rewards += row.count('o') + row.count('?') + row.count('M')
        powerups += row.count('M')
        solid += row.count('X') + row.count('?') + row.count('|') + row.count('T') + row.count('M') + row.count('B')

    negativeSpace = float(len(visited)) / float(empty)
    pathPercentage = float(smallest) / float(empty)
    emptyPercentage = float(empty) / float(totalSize)
    decorationPercentage = (float(pipes) + float(breakable) + float(enemies) + float(rewards)) / float(totalSize)
    leniency = enemies - powerups * 0.5 - 0.5 * rewards + len(gaps)

    solidX = []
    solidY = []
    yy = 0
    for yy in range(maxY):
        xx = 0
        if yy > 0:
            for c in levelStr[yy]:
                if isSolid(c) and not isSolid(levelStr[yy - 1][xx]):
                    # solidPts.append([xx,yy])
                    solidX.append(xx)
                    solidY.append(yy)
                xx += 1
        yy += 1
    x = np.array(solidX)
    y = np.array(solidY)
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    linearity = np.abs(r_value)
    if len(paths) > 0:
        return {'length': maxX,
                'negativeSpace': negativeSpace,
                'pathPercentage': pathPercentage,
                'emptyPercentage': emptyPercentage,
                'decorationPercentage': decorationPercentage,
                'leniency': leniency,
                'meaningfulJumps': float(totalMeaningfulJumps) / float(pathcount),
                'jumps': float(totalJumps) / float(pathcount),
                'meaningfulJumpVariance': float(meaningfulJumpVariance) / float(pathcount),
                'jumpVariance': float(jumpVariance) / float(pathcount),
                'linearity': linearity,
                'solvability': 1.0}
    else:
        return {
            'length': maxX,
            'negativeSpace': negativeSpace,
            'pathPercentage': -1,
            'emptyPercentage': emptyPercentage,
            'decorationPercentage': decorationPercentage,
            'leniency': leniency,
            'meaningfulJumps': -1,
            'jumps': -1,
            'meaningfulJumpVariance': -1,
            'jumpVariance': -1,
            'linearity': linearity,
            'solvability': 0}


if __name__ == "__main__":
    name = sys.argv[1]
    with open(name, 'r') as openFile:
        lines = openFile.readlines()
    print(len(lines), len(lines[0]))
    print(metrics(lines))
