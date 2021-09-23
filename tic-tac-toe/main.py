import argparse
import pickle
from curses import wrapper
from functools import partial

from Config import PATH_TO_SAVE
from GameLoopController import GameLoopController
from TicTacToe import TicTacToe


def load_or_create_game(should_load: bool, area_width: int, area_height: int) -> TicTacToe:
    if PATH_TO_SAVE.exists() and should_load:
        with open(PATH_TO_SAVE, 'rb') as save_file:
            game = pickle.load(save_file)
    else:
        game = TicTacToe(width=area_width, height=area_height)
    return game


def main(args, screen):
    game = load_or_create_game(args.load, args.n, args.k)
    controller = GameLoopController(game, screen)
    controller.run_game_loop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("n", help='width of the playing area', type=int)
    parser.add_argument("k", help='height of the playing area', type=int)
    parser.add_argument("--load", help='loads game from a save file (if this file exists)', action='store_true')
    args = parser.parse_args()

    wrapper(partial(main, args))
