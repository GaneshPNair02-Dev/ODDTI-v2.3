# ==============================================================
# ⚡ ODDTI™ v2.3 — Predictor Edition
# --------------------------------------------------------------
# Developer  : Ganesh P. Nair (⚡GPN⚡)
# Co-Developer (AI Engine): ChatGPT (OpenAI GPT-5)
# Build Date : 2025
# Platform   : Python 3.8+ (PC Edition)
# --------------------------------------------------------------
# © 2025 Ganesh P. Nair. All rights reserved.
#
# LICENSE NOTICE:
# This software is proprietary and distributed for educational
# and personal use only. Commercial use, redistribution, or
# modification of any portion of this code without explicit
# written permission from the author is strictly prohibited.
#
# You may:
#   • Download and run this file for personal, non-commercial use.
#   • Study and learn from the source code for educational purposes.
#
# You may NOT:
#   • Copy, edit, rebrand, or redistribute this code.
#   • Use it in any project, repository, or package without permission.
#   • Claim authorship or modify the copyright notice.
#
# DISCLAIMER:
# This software is provided "as is" without warranty of any kind.
# The author assumes no responsibility for any damage resulting
# from use or misuse of this program.
#
# --------------------------------------------------------------
# OFFICIAL TAGLINE:
#  “The classic Indian bench game, reborn with machine logic.”
# --------------------------------------------------------------
# Official Repository: (to be added after GitHub release)
# ==============================================================

# ODDTI_UI.py  - compact, interactive TI-friendly edition
# Save -> transfer to TI-84 CE Python
import random

VALID = (0,1,2,3,4,5,6)

def prompt_choice(prompt, options):
    opts = [o.lower() for o in options]
    while True:
        r = input(prompt).strip().lower()
        if r in opts:
            return r
        print("Invalid. try:", "/".join(options))

def prompt_num(prompt):
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
        except:
            print("Enter number 0-6")
            continue
        if v in VALID:
            return v
        print("Enter number 0-6")

# ---------- Toss ----------
def do_toss():
    call = prompt_choice("Toss call (odd/even): ", ("odd","even"))
    p = prompt_num("Your toss num 0-6: ")
    c = random.choice(VALID)
    s = p + c
    parity = "even" if s%2==0 else "odd"
    print("You",p,"CPU",c,"Sum:",s,parity)
    if parity == call:
        print("You win toss")
        who = "player"
    else:
        print("CPU wins toss")
        who = "cpu"
    return who

# ---------- Innings (interactive) ----------
def play_innings(batting, target=None):
    # returns (score, ball_log_list)
    score = 0
    ball_log = []  # list of tuples (batter_num, bowler_num, runs_added)
    print("\n--- {} INNINGS ---".format("PLAYER" if batting=="player" else "CPU"))
    while True:
        if batting == "player":
            b = prompt_num("Bat num 0-6: ")
            bowl = random.choice(VALID)
            print("CPU bowls", bowl)
            if b == bowl:
                print("OUT! (you) Last ball:", b, "vs", bowl)
                ball_log.append((b, bowl, 0))
                break
            score += b
            ball_log.append((b, bowl, b))
            print("Runs+", b, "Total:", score)
            if target is not None:
                need = target + 1 - score
                if need <= 0:
                    print("Target achieved! 🎯")
                    break
                print("Need", need, "more")
        else:
            bat = random.choice(VALID)
            bowl = prompt_num("Bowl num 0-6: ")
            print("CPU bats", bat)
            if bat == bowl:
                print("CPU OUT! Last ball:", bat, "vs", bowl)
                ball_log.append((bat, bowl, 0))
                break
            score += bat
            ball_log.append((bat, bowl, bat))
            print("CPU +", bat, "Total:", score)
            if target is not None:
                need = target + 1 - score
                if need <= 0:
                    print("CPU reached target")
                    break
                print("CPU needs", need, "more")
    print("--- innings end. Score:", score, "---\n")
    return score, ball_log

# ---------- display helpers ----------
def print_match_summary(player_score, cpu_score, player_batted_first, log_first=None, log_second=None):
    # show last-ball logs if available (short)
    if log_first or log_second:
        print("\nBall logs (last few balls):")
        if log_first:
            print("Innings 1 last balls:", log_first[-5:])
        if log_second:
            print("Innings 2 last balls:", log_second[-5:])
    print()
    print("\n" + "="*28)
    ord_text = "Player batted 1st" if player_batted_first else "CPU batted 1st"
    print(ord_text)
    print("-"*28)
    print("Player :", player_score)
    print("CPU    :", cpu_score)
    if player_score > cpu_score:
        print("Result : Player wins by", player_score - cpu_score, "runs")
    elif cpu_score > player_score:
        print("Result : CPU wins by", cpu_score - player_score, "runs")
    else:
        print("Result : Match tied")
    print("="*28)

# ---------- Single match ----------
def single_match():
    toss_winner = do_toss()
    if toss_winner == "player":
        pick = prompt_choice("You choose bat or bowl? (bat/bowl): ", ("bat","bowl"))
        player_first = (pick == "bat")
    else:
        comp_choice = random.choice(("bat","bowl"))
        print("CPU chooses to", comp_choice)
        player_first = (comp_choice != "bat")

    if player_first:
        print("You bat first")
        p_score, log1 = play_innings("player")
        print("CPU needs", p_score + 1)
        c_score, log2 = play_innings("computer", target=p_score)
    else:
        print("CPU bats first")
        c_score, log1 = play_innings("computer")
        print("You need", c_score + 1)
        p_score, log2 = play_innings("player", target=c_score)

    print_match_summary(p_score, c_score, player_first, log1, log2)
    # return winner string for series bookkeeping
    if p_score > c_score:
        return "player", p_score, c_score
    elif c_score > p_score:
        return "cpu", p_score, c_score
    else:
        return "tie", p_score, c_score

# ---------- Best-of-3 ----------
def best_of_three():
    p_wins = 0
    c_wins = 0
    matches = []
    for i in range(1,4):
        print("\n=== Match", i, "===")
        winner, p_score, c_score = single_match()
        matches.append((winner, p_score, c_score))
        if winner == "player":
            p_wins += 1
        elif winner == "cpu":
            c_wins += 1
        print("Series:", p_wins, "-", c_wins)
        if p_wins == 2 or c_wins == 2:
            break

    print("\n=== Series summary ===")
    for idx, m in enumerate(matches, start=1):
        w, ps, cs = m
        label = "Player" if w=="player" else "CPU" if w=="cpu" else "Tie"
        print("M{}: {}  {}-{}".format(idx, label, ps, cs))
    if p_wins > c_wins:
        print("Series winner: Player", p_wins, "to", c_wins)
    elif c_wins > p_wins:
        print("Series winner: CPU", c_wins, "to", p_wins)
    else:
        print("Series ended tied", p_wins, "-", c_wins)
    print()

# ---------- Main UI ----------
def main():
    print("=== ODDTI UI v2 (lite interactive) ===")
    while True:
        print("\n1) Single match")
        print("2) Best of 3")
        print("3) Quit")
        ch = input("Choose 1/2/3: ").strip()
        if ch == "1":
            single_match()
        elif ch == "2":
            best_of_three()
        elif ch == "3":
            print("Bye ⚡GPN⚡")
            break
        else:
            print("Invalid")

if __name__ == "__main__":
    main()
#———————————————————————————————————————————

