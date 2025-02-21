import os
import sys
import colorama
from printers import print_commands, print_pretty_comb_list, print_pretty_own

from rumi_api import Player, init_deck, parse_combo_string


def main():
    is_game_played = True
    # game loop (TODO add killswitch to the loop when game won)
    while(is_game_played):
        # global variables that provide data needed for all operations
        global table
        global deck
        global player_list
        global is_compact

        deck = init_deck()
        table = []
        is_compact = False

        # gather game start information
        player_count = player_count_loop()
        player_list = get_player_list(player_count)

        # game logic start point
        players_iterate_loop(player_list)


def player_count_loop():
    '''
    Get data about player count by asking the players for input.
    '''

    while True:
        player_count_input = input('How many players? 1-6 values only\n')
        player_count = 0
        try:
            player_count = int(player_count_input)
        except Exception:
            pass

        if(player_count < 1 or player_count > 6):
            print('incorrect. 1-6 please.')
        else:
            return player_count


def get_player_list(player_count: int):
    '''
    Create a player object with name from input, initialize the player's hand with starter from deck.
    '''

    player_list = []
    for player_num in range(0, player_count):
        name = input(f'Player {player_num+1}, enter your name.\n')
        player = Player(name)
        player.take_starters(deck)
        player_list.append(player)
    return player_list


def players_iterate_loop(player_list: list[Player]):
    '''
    Cyclic iteration of player list. Next player only when player.turn_over is True.
    '''

    idx = 0
    while True:

        if idx >= len(player_list):
            idx = 0

        current_player = player_list[idx]
        _prepare_game_terminal(current_player)
        current_player.turn_over = False
        while not current_player.turn_over:
            player_command_loop(current_player)

        idx += 1


def player_command_loop(player: Player):
    '''
    Get user's input and handle it until the moves don't end the turn
    by marking the player.turn_over falg as True.
    '''

    while not player.turn_over:
        cmd, input_vars = _get_cmd_input()
        _handle_game_commands(cmd, player, input_vars)
        # if no game ending command was given, check util commands
        if not player.turn_over:
            _handle_misc_commands(cmd, player)


def _get_cmd_input():
    '''Get command input from the player.'''

    inp = input(
        "What will you do? (write command + [Enter] to confirm). [H] for help.\n").split(':')

    # Command is followed by ':' symbol.
    cmd = inp.pop(0).upper()
    # TODO after being done with whole game logic, does it ever need to be a list?
    input_vars = []
    for inp in inp:
        input_vars.append(inp.strip())
    return cmd, input_vars

# _______________COMMAND HANDLER_______________


def _handle_game_commands(cmd: str, player: Player, input_vars):
    '''
    Process user command. Check for commands that touch on game logic aspects.
    '''

    if cmd == 'G':
        # grab random and finish command loop √
        if player.moved_this_turn:
            print(
                'Player already moved this round, no need to grab a piece. Press [Q]')
        else:
            player.take_random(deck)
            player.turn_over = True

    if cmd == 'E' and len(input_vars) == 1:
        # enter the game with combos that have 30+ in value, finish command loop √
        # example: "E 12 14 16 | 1 3 5 7"
        enter_table(input_vars[0], player)

    if cmd == 'C' and len(input_vars) == 1:
        # create a new combination, without ending your turn
        create_combination(input_vars[0], player)

    if cmd == 'T':
        # TODO
        # input_vars: "ID_C | A ID_T h/t"
        # add/remove tile to existing (A or R)
        # example: "T: 3 | A 76 t" <- add tile_id=76 to combiantion_id=3 at tail
        modify_combination(input_vars[0], player)


def _handle_misc_commands(cmd: str, player: Player):
    '''
    Process user command. Check for commands that touch on non game-logic related aspects.
    '''

    if cmd == 'Q':
        if player.moved_this_turn:
            # finish command loop. Outer loop changes player to the next one
            player.turn_over = True
        else:
            print(
                'Cant finish the round without any action. Press [G] to grab from deck.')

    if cmd == 'H':
        print_commands()
    if cmd == 'SORT':
        player.sort_tiles()
        _prepare_game_terminal(player)

    if cmd == 'QUIT':
        sys.exit('Quitted..')

    if cmd == 'CLEAR':
        _clean_terminal()
        _print_default_view(player)
    if cmd == 'TOGGLE':
        global is_compact
        is_compact = not is_compact
        _clean_terminal()
        _print_default_view(player)


# _______________COMMAND ACTIONS_______________

def enter_table(user_input: str, player: Player):
    '''
    Parse given data and try to add it to the table.

    Example input:
    '23 25 27 | 1 76 142'
     parse to:
    [['23','25','27'],['1','76','142']]

    Result:
    Print message and/or append the table by taking the tiles from the player.tile_list
     '''

    combination_input_list = user_input.split('|')
    combination_list = []

    for input_tile_list in combination_input_list:
        input_tile_list = input_tile_list.strip()
        combination_list.append(parse_combo_string(
            input_tile_list.strip(), player))

    player.enter_game(combination_list)

    if player.is_out:
        for combo in combination_list:
            table.append(combo)
            player.turn_over = True
    else:
        print('Nope, did not work out.')


def create_combination(user_input, player: Player):
    '''
    Send to API request to create combination and manage the terminal.
    '''

    is_performed = player.create_combination(user_input, table)
    if is_performed:
        _prepare_game_terminal(player)
        print('Added!')
    else:
        print('Invalid move.')


def modify_combination(user_input, player: Player):
    '''
    Send to API request to modify combination and manage the terminal.
    '''

    is_performed = player.modify_combination(user_input, table)
    if is_performed:
        _prepare_game_terminal(player)
        print('Added!')
    else:
        print('Invalid move.')


# _______________UTILS_______________

def _prepare_game_terminal(current_player: Player):
    _clean_terminal()
    global is_compact
    if not is_compact: print(f'{current_player.name}, it\'s your turn!\n')
    # for colorful output
    colorama.init()
    _print_default_view(current_player)


def _clean_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def _print_default_view(current_player: Player):
    global is_compact
    print_pretty_comb_list(table, is_compact)
    print_pretty_own(current_player.tiles, is_compact)


if __name__ == "__main__":
    main()
