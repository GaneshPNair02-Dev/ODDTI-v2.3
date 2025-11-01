# ==========================================================
# ⚡ ODDTI™ v2.3 + CPU Predictor — "Odd/Even Hand Cricket"
# Integrated Predictor by ChatGPT for Ganesh P. Nair
# Compatible: TI-84 Plus CE Python, Thonny, PyCharm
# ==========================================================

import random
import sys

VALID_NUMS = [0, 1, 2, 3, 4, 5, 6]

# -----------------------------
# Predictor: frequency + 1-step Markov
# -----------------------------
# Lightweight, in-memory learning. No external libs.
# Usage:
#   pred = Predictor()
#   pred.predict(last_player_move) -> most likely next player move (0-6)
#   pred.update(prev_move, actual_move) -> update counts after observing actual_move
# -----------------------------
class Predictor:
    def __init__(self):
        # overall frequency counts of player's numbers
        self.freq = {n: 1 for n in VALID_NUMS}  # init with 1 for Laplace smoothing
        # markov: previous -> counts of next
        self.markov = {prev: {n: 1 for n in VALID_NUMS} for prev in VALID_NUMS}
        self.last_player_move = None

    def predict(self, prev=None):
        """
        Predict player's next number given prev (last move).
        Returns an integer 0-6 (most likely).
        Uses markov if prev provided and seen, else overall freq.
        """
        if prev is None:
            prev = self.last_player_move

        if prev is not None and prev in self.markov:
            counts = self.markov[prev]
            # choose highest-count key; break ties randomly
            max_count = max(counts.values())
            candidates = [k for k, v in counts.items() if v == max_count]
            return random.choice(candidates)
        else:
            counts = self.freq
            max_count = max(counts.values())
            candidates = [k for k, v in counts.items() if v == max_count]
            return random.choice(candidates)

    def update(self, prev, actual):
        """
        Update predictor after we observe actual player's number.
        prev may be None on first seen move.
        """
        if actual not in VALID_NUMS:
            return
        # update frequencies
        self.freq[actual] = self.freq.get(actual, 0) + 1
        # update markov if prev provided
        if prev is not None and prev in self.markov:
            self.markov[prev][actual] = self.markov[prev].get(actual, 0) + 1
        # update last seen
        self.last_player_move = actual

    def reset(self):
        self.__init__()


# Global predictor instance and config
USE_PREDICTOR = True        # toggle predictor on/off
PREDICTOR_EPSILON = 0.12    # probability CPU ignores predictor (randomize)
predictor = Predictor()

# -----------------------------
# Input helpers
# -----------------------------

def input_choice(prompt, options):
    opts = [o.lower() for o in options]
    while True:
        resp = input(prompt).strip().lower()
        if resp in opts:
            return resp
        print("Invalid choice. Options:", ", ".join(options))

def input_int_in_set(prompt, valid_set):
    while True:
        try:
            val = int(input(prompt).strip())
        except ValueError:
            print("Please enter an integer.")
            continue
        if val in valid_set:
            return val
        print("Value must be one of:", sorted(valid_set))

# -----------------------------
# Toss phase
# -----------------------------

def choose_odd_or_even():
    return input_choice("Choose odd or even for toss? (odd/even): ", ("odd", "even"))

def player_choose_number():
    return input_int_in_set("Enter your toss number (0–6): ", set(VALID_NUMS))

def toss(player_parity):
    print("\n--- TOSS ---")
    player_num = player_choose_number()
    comp_num = random.choice(VALID_NUMS)
    print(f"You: {player_num}, Computer: {comp_num}")
    s = player_num + comp_num
    result_parity = "even" if s % 2 == 0 else "odd"
    print(f"Sum = {s} → {result_parity}")
    if result_parity == player_parity:
        print("You win the toss!")
        return "player"
    print("Computer wins the toss!")
    return "computer"

# -----------------------------
# CPU choice wrappers using predictor
# -----------------------------
def cpu_choose_when_bowling(prev_player_move):
    """
    CPU is bowling (player batting). CPU should try to predict player's chosen bat
    and pick that number to get an OUT. If predictor disabled or epsilon triggers,
    pick random.
    """
    if USE_PREDICTOR and random.random() > PREDICTOR_EPSILON:
        pred = predictor.predict(prev_player_move)
        # choose predicted value (aggressive)
        return pred
    else:
        return random.choice(VALID_NUMS)

def cpu_choose_when_batting(prev_player_move):
    """
    CPU is batting (player bowling). CPU would like to avoid being out:
    predict player's likely bowl, and pick a different number to avoid equality.
    Also bias toward higher scoring numbers for competitiveness.
    """
    if USE_PREDICTOR and random.random() > PREDICTOR_EPSILON:
        pred = predictor.predict(prev_player_move)
        # choose a number != pred, prefer higher numbers but keep some randomness
        candidates = [n for n in VALID_NUMS if n != pred]
        # weight by value: replicate values so larger numbers slightly more likely
        weighted = []
        for n in candidates:
            weight = 1 + n  # simple weight: 1..7
            weighted.extend([n] * weight)
        return random.choice(weighted)
    else:
        return random.choice(VALID_NUMS)

# -----------------------------
# Innings logic (uses predictor)
# -----------------------------

def play_innings(batting, target=None):
    score = 0
    print(f"\n--- {batting.upper()} INNINGS START ---")
    prev_player_move = predictor.last_player_move  # help predictor by providing last seen
    while True:
        if batting == "player":
            p = input_int_in_set("Enter your number (0–6): ", set(VALID_NUMS))
            # CPU selects bowl: try to guess player's number (to get out)
            c = cpu_choose_when_bowling(prev_player_move)
            print(f"Computer bowls: {c}")
            # update predictor with player's move after we observe it (for next ball)
            predictor.update(prev_player_move, p)
            prev_player_move = p
            if p == c:
                print("You're OUT!")
                break
            # scoring rule per your mod: only player's number counts (you changed earlier)
            score += p
            print(f"Runs this ball: {p} | Total: {score}")
            if target is not None:
                runs_left = target + 1 - score
                if runs_left <= 0:
                    print("Target achieved! 🎯")
                    break
                else:
                    print(f"Runs required: {runs_left}")
        else:
            # Computer is batting
            # CPU selects own bat number (tries to avoid being out using predictor)
            c = cpu_choose_when_batting(prev_player_move)
            # player bowls
            p = input_int_in_set("Enter your bowl number (0–6): ", set(VALID_NUMS))
            print(f"Computer bats: {c}")
            # update predictor with player's bowl (player's action)
            predictor.update(prev_player_move, p)
            prev_player_move = p
            if c == p:
                print("Computer is OUT!")
                break
            # scoring rule: only CPU's number counts when CPU batting
            score += c
            print(f"Computer runs this ball: {c} | Total: {score}")
            if target is not None:
                runs_left = target + 1 - score
                if runs_left <= 0:
                    print("Computer reached the target! 🏏")
                    break
                else:
                    print(f"Computer needs {runs_left} runs more.")
    print(f"--- {batting.upper()} INNINGS END: Score = {score} ---\n")
    return score

# -----------------------------
# Scorecard + match handling
# -----------------------------

def display_scorecard(player_score, computer_score, player_batted_first):
    print("\n" + "="*36)
    if player_batted_first:
        print("Innings order: Player batted first  →  Computer chased")
    else:
        print("Innings order: Computer batted first  →  Player chased")
    print("-"*36)
    print(f"Player score    : {player_score}")
    print(f"Computer score  : {computer_score}")
    print("-"*36)
    if player_score > computer_score:
        print(f"Result: Player wins by {player_score - computer_score} runs.")
    elif computer_score > player_score:
        print(f"Result: Computer wins by {computer_score - player_score} runs.")
    else:
        print("Result: Match tied!")
    print("="*36 + "\n")

def bat_or_ball_choice_for_player():
    return input_choice("You won toss. Choose to bat or bowl? (bat/bowl): ", ("bat", "bowl"))

def single_match():
    # Toss
    player_parity = choose_odd_or_even()
    toss_winner = toss(player_parity)

    if toss_winner == "player":
        choice = bat_or_ball_choice_for_player()
        player_bats_first = (choice == "bat")
    else:
        comp_choice = random.choice(("bat", "bowl"))
        print(f"Computer chooses to {comp_choice}.")
        player_bats_first = (comp_choice != "bat")

    if player_bats_first:
        print("You bat first.")
        player_first_score = play_innings("player")
        print(f"Computer needs {player_first_score + 1} to win.")
        computer_second_score = play_innings("computer", target=player_first_score)
        player_score = player_first_score
        computer_score = computer_second_score
    else:
        print("Computer bats first.")
        computer_first_score = play_innings("computer")
        print(f"You need {computer_first_score + 1} to win.")
        player_second_score = play_innings("player", target=computer_first_score)
        computer_score = computer_first_score
        player_score = player_second_score

    display_scorecard(player_score, computer_score, player_bats_first)
    return player_score, computer_score, player_bats_first

def best_of_three():
    player_wins = 0
    comp_wins = 0
    match_no = 0

    while match_no < 3 and player_wins < 2 and comp_wins < 2:
        match_no += 1
        print(f"\n=== SERIES: Match {match_no}/3 ===")
        p_score, c_score, p_batted_first = single_match()
        if p_score > c_score:
            player_wins += 1
            print(f"Match {match_no} Winner: Player")
        elif c_score > p_score:
            comp_wins += 1
            print(f"Match {match_no} Winner: Computer")
        else:
            print(f"Match {match_no}: Tie (no points)")
        print(f"Series so far: Player {player_wins} - Computer {comp_wins}")

    print("\n=== SERIES COMPLETE ===")
    if player_wins > comp_wins:
        print(f"You win the series {player_wins} - {comp_wins}! 🏆")
    elif comp_wins > player_wins:
        print(f"Computer wins the series {comp_wins} - {player_wins}! 🤖")
    else:
        print("Series tied overall.")
    print("========================\n")

# -----------------------------
# CLI helper to manage predictor
# -----------------------------

def predictor_menu():
    global USE_PREDICTOR, PREDICTOR_EPSILON, predictor
    while True:
        print("\n-- Predictor Menu --")
        print(f"(1) Toggle predictor (currently {'ON' if USE_PREDICTOR else 'OFF'})")
        print(f"(2) Epsilon (randomness) = {PREDICTOR_EPSILON:.2f}")
        print("(3) Reset predictor memory")
        print("(4) Show top frequencies")
        print("(5) Back")
        ch = input("Choose: ").strip()
        if ch == "1":
            USE_PREDICTOR = not USE_PREDICTOR
            print("Predictor now", "ON" if USE_PREDICTOR else "OFF")
        elif ch == "2":
            v = input("Enter epsilon (0.0 - 0.9 suggested): ").strip()
            try:
                vv = float(v)
                PREDICTOR_EPSILON = max(0.0, min(0.9, vv))
                print("Epsilon set to", PREDICTOR_EPSILON)
            except:
                print("Invalid number.")
        elif ch == "3":
            predictor.reset()
            print("Predictor memory reset.")
        elif ch == "4":
            print("Overall freq:", predictor.freq)
            # show markov for last seen (if any)
            if predictor.last_player_move is not None:
                print("Markov row for last seen (", predictor.last_player_move, "):", predictor.markov[predictor.last_player_move])
            else:
                print("No last move yet.")
        else:
            break

# -----------------------------
# Main menu
# -----------------------------

def main():
    print("=== ⚡ ODDTI™ v2.3 (Predictor edition) ===")
    while True:
        print("\n(1) Single Match")
        print("(2) Best of 3 Series")
        print("(3) Predictor Menu")
        print("(4) Quit")
        choice = input("Choose (1/2/3/4): ").strip()
        if choice == "1":
            single_match()
        elif choice == "2":
            best_of_three()
        elif choice == "3":
            predictor_menu()
        else:
            print("Exiting. ⚡GPN⚡ out.")
            break

# -----------------------------
# Program entry
# -----------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Bye!")
        sys.exit(0)