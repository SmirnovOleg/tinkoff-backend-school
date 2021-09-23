import curses
import pickle
from typing import Optional

import ScreenComponents
from Config import PATH_TO_SAVE
from PlayingArea import CellState
from TicTacToe import TicTacToe, States, FailedTurnError


class GameLoopController:
    def __init__(self, game: TicTacToe, screen):
        self.game = game
        self.screen = screen
        self.__required_screen_height = \
            ScreenComponents.WELCOME_HEIGHT + game.area.height + 1 + ScreenComponents.INSTRUCTIONS_HEIGHT + 1

    def run_game_loop(self):

        while True:

            # Check if screen is large enough to play game
            screen_height, _ = self.screen.getmaxyx()
            if screen_height < self.__required_screen_height:
                raise KeyError("Please make your terminal screen larger.")

            if self.game.state == States.USER_TURN:
                instructions_y = self.__prepare_screen_for_user_turn()

                # Perform interactions with user: move the cursor across the field
                char = self.screen.getch()
                if char == curses.KEY_UP:
                    self.game.area.cursor.move_up()
                elif char == curses.KEY_DOWN:
                    self.game.area.cursor.move_down()
                elif char == curses.KEY_LEFT:
                    self.game.area.cursor.move_left()
                elif char == curses.KEY_RIGHT:
                    self.game.area.cursor.move_right()

                elif char == ord(' '):
                    # Perform interactions with user: set `X` on the PlayingArea
                    try:
                        self.game.user_turn()
                        self.game.state = States.WINNER_CHECKING
                    except FailedTurnError as e:
                        error_message_y = instructions_y + ScreenComponents.INSTRUCTIONS_HEIGHT
                        self.screen.addstr(error_message_y, 0, str(e))

                elif char == ord('s'):
                    # Save and quit
                    with open(PATH_TO_SAVE, 'wb') as save_file:
                        pickle.dump(self.game, save_file)
                    return

                elif char == ord('q'):
                    # Just quit
                    return

            elif self.game.state == States.AI_TURN:
                self.screen.clear()
                try:
                    self.game.ai_turn()
                    self.game.state = States.WINNER_CHECKING
                except FailedTurnError:
                    self.game.state = States.DRAW

            elif self.game.state == States.WINNER_CHECKING:
                winner = self.game.find_winner()
                self.__switch_state_according_to_winner(winner)

            elif self.game.state == States.X_WIN:
                self.__display_outcome(f'{CellState.X} win!\n')

            elif self.game.state == States.O_WIN:
                self.__display_outcome(f'{CellState.O} win!\n')

            elif self.game.state == States.DRAW:
                self.__display_outcome('Draw!\n')

            elif self.game.state == States.CONTINUE:
                char = self.screen.getch()
                if char == ord('p'):
                    self.game.refresh()
                    self.screen.clear()
                elif char == ord('q'):
                    return

    def __switch_state_according_to_winner(self, winner: Optional[str]):
        if not winner:
            if not self.game.area.empty_cells:
                self.game.state = States.DRAW
            elif self.game.prev_turn == CellState.X:
                self.game.state = States.AI_TURN
            elif self.game.prev_turn == CellState.O:
                self.game.state = States.USER_TURN
        elif winner == CellState.X:
            self.game.state = States.X_WIN
        elif winner == CellState.O:
            self.game.state = States.O_WIN

    def __prepare_screen_for_user_turn(self) -> int:
        curses.curs_set(0)
        self.screen.addstr(0, 0, ScreenComponents.WELCOME_STR)
        self.screen.addstr(ScreenComponents.WELCOME_HEIGHT, 0, str(self.game.area))

        i, j = self.game.area.cursor.i, self.game.area.cursor.j
        self.screen.addstr(i + ScreenComponents.WELCOME_HEIGHT, j, self.game.area.get_symbol(i, j), curses.A_STANDOUT)

        instructions_y = ScreenComponents.WELCOME_HEIGHT + self.game.area.height + 1
        self.screen.addstr(instructions_y, 0, ScreenComponents.INSTRUCTIONS_STR)

        return instructions_y

    def __display_outcome(self, outcome_message: str):
        self.screen.clear()
        self.screen.addstr(0, 0, ScreenComponents.WELCOME_STR)
        self.screen.addstr(ScreenComponents.WELCOME_HEIGHT, 0, str(self.game.area))
        self.screen.addstr(ScreenComponents.WELCOME_HEIGHT + self.game.area.height + 1, 0,
                           outcome_message + ScreenComponents.CONTINUE_INSTRUCTIONS_STR)
        self.game.state = States.CONTINUE
