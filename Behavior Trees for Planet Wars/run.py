import subprocess
import os, sys


def show_match(bot, opponent_bot, map_num):
    """
        Runs an instance of Planet Wars between the two given bots on the specified map. After completion, the
        game is replayed via a visual interface.
    """
    command = 'java -jar tools/PlayGame.jar maps/map' + str(map_num) + '.txt 1000 1000 log.txt ' + \
              '"python ' + bot + '" ' + \
              '"python ' + opponent_bot + '" ' + \
              '| java -jar tools/ShowGame.jar'
    print(command)
    os.system(command)


def test(bot, opponent_bot, map_num):
    """ Runs an instance of Planet Wars between the two given bots on the specified map. """
    bot_name, opponent_name = bot.split('/')[1].split('.')[0], opponent_bot.split('/')[1].split('.')[0]
    print('Running test:',bot_name,'vs',opponent_name)
    command = 'java -jar tools/PlayGame.jar maps/map' + str(map_num) +'.txt 1000 1000 log.txt ' + \
              '"python ' + bot + '" ' + \
              '"python ' + opponent_bot + '" '

    print(command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    while True:
        return_code = p.poll()  # returns None while subprocess is running
        line = p.stdout.readline().decode('utf-8')
        if '1 timed out' in line:
            print(bot_name,'timed out.')
            break
        elif '2 timed out' in line:
            print(opponent_name,'timed out.')
            break
        elif '1 crashed' in line:
            print(bot_name, 'crashed.')
            break
        elif '2 crashed' in line:
            print(opponent_name, 'crashed')
            break
        elif 'Player 1 Wins!' in line:
            print(bot_name,'wins!')
            break
        elif 'Player 2 Wins!' in line:
            print(opponent_name,'wins!')
            break

        if return_code is not None:
            break


if __name__ == '__main__':
    path =  os.getcwd()
    opponents = ['opponent_bots/easy_bot.py',
                 'opponent_bots/spread_bot.py',
                 'opponent_bots/aggressive_bot.py',
                 'opponent_bots/defensive_bot.py',
                 'opponent_bots/production_bot.py']

    maps = [71, 13, 24, 56, 7]

    my_bot = 'behavior_tree_bot/bt_bot.py'
    show = len(sys.argv) < 2 or sys.argv[1] == "show"
    for opponent, map in zip(opponents, maps):
        # use this command if you want to observe the bots
        if show:
            show_match(my_bot, opponent, map)
        else:
            # use this command if you just want the results of the matches reported
            test(my_bot, opponent, map)
