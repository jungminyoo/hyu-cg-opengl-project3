# console_controller.py
import random
import threading
import time


class DanceBattleSystem:
    """
    Console-based dance battle system.

    whos_dancing:
        0 = nobody
        1 = user
        2 = computer
        3 = both
    """

    STATE_WAIT_USER_INPUT = "WAIT_USER_INPUT"
    STATE_USER_DANCING = "USER_DANCING"
    STATE_USER_REVEAL = "USER_REVEAL"
    STATE_COMPUTER_DANCING = "COMPUTER_DANCING"
    STATE_COMPUTER_REVEAL = "COMPUTER_REVEAL"
    STATE_ROUND_RESULT = "ROUND_RESULT"
    STATE_WAIT_NEXT_ROUND = "WAIT_NEXT_ROUND"
    STATE_WAIT_RESTART = "WAIT_RESTART"

    def __init__(self, dance_names: list[str], max_rounds: int = 3):
        # system initialization
        self._dance_names = dance_names
        self._max_rounds = max_rounds

        self._input = None
        self._turn = 1
        self._user_score = 0
        self._computer_score = 0

        self._computer_choice = None
        self._user_choice = None

        self._current_user_choice = None
        self._current_computer_choice = None

        self._whos_dancing = 0
        self._state = self.STATE_WAIT_USER_INPUT
        self._state_started_at = time.time()

        self._is_finished = False
        self._should_quit = False
        self._round_winner = None
        self._final_winner = None

        self._print_rules()
        input("If you understood the rules, press Enter to start the game.")

        self._start_game()
        self._start_input_thread()

    # -------------------------
    # Input Thread
    # -------------------------
    def _start_input_thread(self):
        thread = threading.Thread(target=self._input_loop, daemon=True)
        thread.start()

    def _input_loop(self):
        while True:
            cmd = input("> ").strip().lower()
            if self._input is None:
                self._input = cmd

    def _consume_input(self):
        cmd = self._input
        self._input = None
        return cmd

    # -------------------------
    # Game Flow
    # -------------------------
    def _start_game(self):
        self._turn = 1
        self._user_score = 0
        self._computer_score = 0
        self._is_finished = False
        self._final_winner = None
        self._start_turn()

    def _start_turn(self):
        self._user_choice = None
        self._computer_choice = random.choice(self._dance_names)

        self._current_user_choice = None
        self._current_computer_choice = None
        self._round_winner = None
        self._whos_dancing = 0

        self._change_state(self.STATE_WAIT_USER_INPUT)
        self._print_menu()

    def update(self):
        cmd = self._consume_input()

        if cmd is not None:
            self._handle_command(cmd)

        now = time.time()
        elapsed = now - self._state_started_at

        if self._state == self.STATE_USER_DANCING:
            if elapsed >= 15.0:
                self._print_gap()
                print("----------------------------------")
                print(f"User selected [{self._user_choice}]!")
                print("----------------------------------")
                self._change_state(self.STATE_USER_REVEAL)

        elif self._state == self.STATE_USER_REVEAL:
            if elapsed >= 3.0:
                self._print_gap()
                print("----------------------------------")
                print("Computer is dancing... (15s)")
                print("----------------------------------")
                self._current_computer_choice = self._computer_choice
                self._whos_dancing = 3
                self._change_state(self.STATE_COMPUTER_DANCING)

        elif self._state == self.STATE_COMPUTER_DANCING:
            if elapsed >= 15.0:
                self._print_gap()
                print("----------------------------------")
                print(f"Computer selected [{self._computer_choice}]!")
                print("----------------------------------")
                self._change_state(self.STATE_COMPUTER_REVEAL)

        elif self._state == self.STATE_COMPUTER_REVEAL:
            if elapsed >= 3.0:
                self._judge_and_print_round_result()
                self._change_state(self.STATE_ROUND_RESULT)

        elif self._state == self.STATE_ROUND_RESULT:
            if elapsed >= 0.5:
                if self._turn >= self._max_rounds:
                    self._finish_game()
                else:
                    print("Press Enter to proceed to the next round.")
                    self._change_state(self.STATE_WAIT_NEXT_ROUND)

    def _handle_command(self, cmd: str):
        if cmd == "q":
            self._should_quit = True
            return

        if cmd == "r":
            self.restart()
            return

        if cmd == "f":
            self._finish_game(force=True)
            return

        if self._state == self.STATE_WAIT_USER_INPUT:
            if cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(self._dance_names):
                    self._select_user_dance(self._dance_names[idx])
                else:
                    print("Invalid dance number.")
            else:
                print("Invalid input. Choose a dance number, r, f, or q.")

        elif self._state == self.STATE_WAIT_NEXT_ROUND:
            if cmd == "":
                self._turn += 1
                self._start_turn()
            else:
                print("Press Enter to proceed to the next round.")

        elif self._state == self.STATE_WAIT_RESTART:
            if cmd == "":
                self.restart()
            else:
                print("Press Enter to restart the game.")

        else:
            print("Please wait until the current dance sequence ends.")

    def _select_user_dance(self, dance_name: str):
        self._user_choice = dance_name
        self._current_user_choice = dance_name

        self._print_gap()
        print("----------------------------------")
        print("User is dancing... (15s)")
        print("----------------------------------")
        self._whos_dancing = 1
        self._change_state(self.STATE_USER_DANCING)

    def _judge_and_print_round_result(self):
        result = self._judge_round(self._user_choice, self._computer_choice)

        if result == 1:
            self._user_score += 1
            self._round_winner = "User"
        elif result == -1:
            self._computer_score += 1
            self._round_winner = "Computer"
        else:
            self._round_winner = "Draw"

        self._print_gap()
        print("\n---------- Round Result ----------")
        print(f"User Dance: {self._user_choice}")
        print(f"Computer Dance: {self._computer_choice}")
        print(f"The winner of this round is [{self._round_winner}]!")
        print(f"Score | Computer {self._computer_score} : User {self._user_score}")
        print("----------------------------------")

    def _finish_game(self, force: bool = False):
        self._is_finished = True
        self._whos_dancing = 0

        if force:
            self._final_winner = "None"
            self._print_gap()
            print("\n========== Game Finished ==========")
            print("The game was force-finished.")
        else:
            if self._user_score > self._computer_score:
                self._final_winner = "User"
            elif self._computer_score > self._user_score:
                self._final_winner = "Computer"
            else:
                self._final_winner = "Draw"
            
            self._print_gap()
            print("\n========== Game Over ==========")
            print(f"Final Score | Computer {self._computer_score} : User {self._user_score}")
            print(f"[{self._final_winner}] is the final winner!")

        print("Press Enter to restart the game.")
        print("================================")
        self._change_state(self.STATE_WAIT_RESTART)

    def restart(self):
        self._print_gap()
        print("\nRestarting the game...")
        self._start_game()

    def _change_state(self, new_state: str):
        self._state = new_state
        self._state_started_at = time.time()

    # -------------------------
    # Rules
    # -------------------------
    def _judge_round(self, user_dance: str, computer_dance: str) -> int:
        """
        return:
            1  = user wins
            0  = draw
            -1 = computer wins
        """

        beats = {
            "HipHop": ["ChaCha", "Zumba"],
            "ChaCha": ["Zumba", "Salsa"],
            "Zumba": ["Salsa", "Reggaeton"],
            "Salsa": ["Reggaeton", "HipHop"],
            "Reggaeton": ["HipHop", "ChaCha"],
        }

        if user_dance == computer_dance:
            return 0

        if computer_dance in beats[user_dance]:
            return 1

        return -1

    def _print_rules(self):
        self._print_gap()
        print("========== Dance Battle Rules ==========")
        print("Choose one of the five dances.")
        print("1. HipHop")
        print("2. ChaCha")
        print("3. Zumba")
        print("4. Salsa")
        print("5. Reggaeton")
        print()
        print("Each dance beats exactly two dances and loses to two dances.")
        print("If both players choose the same dance, the round is a draw.")
        print()
        print("HipHop beats ChaCha and Zumba.")
        print("ChaCha beats Zumba and Salsa.")
        print("Zumba beats Salsa and Reggaeton.")
        print("Salsa beats Reggaeton and HipHop.")
        print("Reggaeton beats HipHop and ChaCha.")
        print()
        print("The player with the higher score after 3 rounds wins the game.")
        print("========================================")

    def _print_tiny_rules(self):
        print("HipHop > ChaCha, Zumba")
        print("ChaCha > Zumba, Salsa")
        print("Zumba > Salsa, Reggaeton")
        print("Salsa > Reggaeton, HipHop")
        print("Reggaeton > HipHop, ChaCha")

    def _print_menu(self):
        self._print_gap()
        print("\n========== Dance Battle Simulator ==========")
        print(f"Round {self._turn} / {self._max_rounds}")
        print(f"Score | Computer {self._computer_score} : User {self._user_score}")
        print("--------------------------------------------")
        self._print_tiny_rules()
        print("--------------------------------------------")
        print("Choose your dance:")
        for i, name in enumerate(self._dance_names, start=1):
            print(f"{i}. {name}")
        print("--------------------------------------------")
        print("r: restart | f: finish | q: quit")
        print("============================================")

    def _print_gap(self):
        print()
        print()
        print()
        print()
        print()
        print()
        print()
        print()
        print()
        print()
        print()

    # -------------------------
    # Properties for main.py
    # -------------------------
    @property
    def turn(self): return self._turn

    @property
    def user_score(self): return self._user_score

    @property
    def computer_score(self): return self._computer_score

    @property
    def computer_choice(self): return self._computer_choice

    @property
    def user_choice(self): return self._user_choice

    @property
    def current_user_choice(self): return self._current_user_choice

    @property
    def current_computer_choice(self): return self._current_computer_choice

    @property
    def whos_dancing(self): return self._whos_dancing

    @property
    def state(self): return self._state

    @property
    def round_winner(self): return self._round_winner

    @property
    def final_winner(self): return self._final_winner

    @property
    def is_finished(self): return self._is_finished

    @property
    def should_quit(self): return self._should_quit