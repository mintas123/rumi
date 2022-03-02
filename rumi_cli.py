from printers import *
from rumi_api import *
import os
import sys
import colorama


def main():
    is_game_played = True
    # game loop (todo add kill to the loop when game won)
    while(is_game_played):
        # global variables that provide data needed for all operations
        global table
        global deck
        global player_list

        deck = init_deck()
        table = []

        # gather game start information
        player_count = player_count_loop()
        player_list = get_player_list(player_count)

        # game logic start point
        players_iterate_loop(player_list)


# get data how many players will be playing
def player_count_loop():
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


def players_iterate_loop(player_list: List[Player]):
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
    '''Get Input from the player.'''

    inp = input(
        "What will you do? (write command + [Enter] to confirm). 'H' for help.\n").split(':')

    # Command is followed by ':' symbol. Input_vars can be a list, as each subcommand is also followed by ':'.
    cmd = inp.pop(0).upper()
    input_vars = []
    for inp in inp:
        input_vars.append(inp.strip())
    return cmd, input_vars

# _______________COMMAND HANDLER_______________


def _handle_game_commands(cmd: str, player: Player, input_vars):
    '''
    Process user command. Check for commands that touch on game logic aspects.
    '''

    if cmd == 'T':
        # take random and finish command loop √
        # TODO verify that no action was performed this loop.
        player.take_random(deck)
        player.turn_over = True

    if cmd == 'E' and len(input_vars) == 1:
        # Enter the game with combos that have 30+ in value, finish command loop √
        enter_table(input_vars[0], player)

    if cmd == 'C' and len(input_vars) == 1:
        # create a new combination, without ending your turn
        create_combination(input_vars[0], player)

    if cmd == 'T' and len(input_vars) == 2:
        # TODO NEXT add/remove tile to existing (A: | R:)
        pass


def _handle_misc_commands(cmd: str, player: Player):
    '''
    Process user command. Check for commands that touch on non game-logic related aspects.
    '''

    if cmd == 'Q':
        # finish command loop. Outer loop changes player to the next one
        player.turn_over = True

    if cmd == 'H':
        print_commands()

    if cmd == 'QUIT':
        sys.exit('Quitted..')

    if cmd == 'CLEAR':
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
        combination_list.append(_parse_combo_string(
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
    Parse and add given combination to the table, by taking the tiles from player.tile_list
    '''

    if player.is_out:
        table.append(_parse_combo_string(user_input, player))
        _prepare_game_terminal(player)
        print('Added!')


# _______________UTILS_______________

def _prepare_game_terminal(current_player: Player):
    _clean_terminal()
    print(f'{current_player.name}, it\'s your turn!\n')
    # for colorful output
    colorama.init()
    _print_default_view(current_player)


def _clean_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def _print_default_view(current_player: Player):
    print_pretty_comb_list(table)
    print_pretty_own(current_player.tiles)


def _parse_combo_string(combo_string: str, player: Player) -> Combination:
    tile_list = []
    tile_id_list = combo_string.split(' ')

    for tile_id in tile_id_list:
        tile_list.append(player.take_from_own_list(tile_id))
    return _create_combo(player, tile_list)


def _create_combo(player: Player, tile_list: List[Tile]):
    try:
        combo = Combination(tile_list)
        return combo
    except ValueError as ve:
        for tile in tile_list:
            player.return_to_own_list(tile)
        print(str(ve))


if __name__ == "__main__":
    main()
