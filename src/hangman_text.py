################################################################################
# File name:    main.py
# Author:       YOUR NAME HERE
# Date:         5/14/2025
# Class:        CS 170
# Assignment:   01Lab
# Purpose:      Demonstrate Codespaces & Python
# Hours:        1.5
################################################################################

"""Supplied text-based Hangman interface.

Run from the src folder: python hangman.py
"""

from hangman_logic import (
    MAX_MISSES,
    is_correct,
    record_guess,
    show_word,
    count_misses,
    is_won,
    is_lost,
    calculate_score,
    get_words_by_difficulty,
    select_category,
    load_categories,
    load_scores,
    save_scores,
    new_round,
)


# ------------------------------------------------------------
# Supplied text interface
# ------------------------------------------------------------


def draw_hangman(iMisses: int) -> None:
    """Print the Hangman figure for the number of misses.

    Args:
        iMisses (int): number of incorrect guesses, from 0 to 6

    Returns:
        None.
    """
    print("      +------+")
    print("      |      |")

    if iMisses >= 1:
        print("      O      |")
    else:
        print("             |")

    sArms: str = "             |"
    if iMisses == 2:
        sArms = "      |      |"
    elif iMisses == 3:
        sArms = "     /|      |"
    elif iMisses >= 4:
        sArms = "     /|\\     |"
    print(sArms)

    if iMisses == 5:
        print("     /       |")
    elif iMisses >= 6:
        print("     / \\     |")
    else:
        print("             |")

    print("             |")
    print("   ==========")


def choose_settings(dCategories: dict[str, list[str]]) -> tuple[str, str]:
    """Ask the player to choose an available category and difficulty.

    Args:
        dCategories (dict[str, list[str]]): categories and their words

    Returns:
        The selected category and difficulty as a tuple.
    """
    lCategories: list[str] = sorted(dCategories)
    lDifficulties: list[str] = ["EASY", "MEDIUM", "HARD"]
    sCategory: str = ""
    sDifficulty: str = ""

    while sCategory == "":
        print("\nChoose a category:")
        for iIndex in range(len(lCategories)):
            print(str(iIndex + 1) + ". " + lCategories[iIndex].title())

        sChoice: str = input("Selection: ").strip()
        if sChoice.isdigit():
            iChoice: int = int(sChoice)
            if iChoice >= 1 and iChoice <= len(lCategories):
                sCategory = lCategories[iChoice - 1]

        if sCategory == "":
            print("Please choose a listed number.")

    while sDifficulty == "":
        print("\nChoose difficulty:")
        print("1. Easy   (4-5 letters)")
        print("2. Medium (6-7 letters)")
        print("3. Hard   (8-10 letters)")
        sChoice = input("Selection: ").strip()

        if sChoice.isdigit():
            iChoice = int(sChoice)
            if iChoice >= 1 and iChoice <= 3:
                sCandidate: str = lDifficulties[iChoice - 1]
                lWords: list[str] = select_category(dCategories, sCategory)
                lWords = get_words_by_difficulty(lWords, sCandidate)
                if len(lWords) > 0:
                    sDifficulty = sCandidate
                else:
                    print("No words available for that combination.")

        if sDifficulty == "" and not sChoice.isdigit():
            print("Please choose 1, 2, or 3.")

    return sCategory, sDifficulty


def display_round(dGame: dict, dScores: dict[str, int]) -> None:
    """Print the current word, guesses, figure, and scores.

    Args:
        dGame (dict): current round state
        dScores (dict[str, int]): cumulative scores

    Returns:
        None.
    """
    sWord: str = dGame["word"]
    lGuesses: list[str] = dGame["guesses"]
    iMisses: int = count_misses(sWord, lGuesses)

    print("\n" + "=" * 34)
    print("CS170 - HANGMAN")
    print(
        "Wins:",
        dScores["wins"],
        " Losses:",
        dScores["losses"],
        " Points:",
        dScores["points"],
    )
    print("Category:", dGame["category"].title())
    print("Difficulty:", dGame["difficulty"].title())
    print()
    draw_hangman(iMisses)
    print("\nWord: ", show_word(sWord, lGuesses))
    print("Guessed letters:", ", ".join(lGuesses))
    print("Incorrect guesses:", iMisses, "of", MAX_MISSES)
    print(dGame["message"])


def play_round(dGame: dict, dScores: dict[str, int]) -> bool:
    """Play one round and update the scores when it finishes.

    Args:
        dGame (dict): current round state
        dScores (dict[str, int]): cumulative scores to update

    Returns:
        True if the round was completed; False if the player quit early.
    """
    sWord: str = dGame["word"]
    lGuesses: list[str] = dGame["guesses"]

    while not dGame["finished"]:
        display_round(dGame, dScores)
        sLetter: str = \
            input("\nEnter a letter (or QUIT to quit): ").strip().upper()

        if sLetter == "QUIT":
            return False

        bAdded: bool = record_guess(lGuesses, sLetter)

        if not bAdded:
            dGame["message"] = "Enter a new letter from A to Z."
        elif is_won(sWord, lGuesses):
            dGame["finished"] = True
            iMisses: int = count_misses(sWord, lGuesses)
            iPoints: int = calculate_score(sWord, iMisses, dGame["difficulty"])
            dScores["wins"] += 1
            dScores["points"] += iPoints
            dGame["message"] = "Congratulations! You won! +" + str(iPoints) + \
                " points."
        elif is_lost(sWord, lGuesses):
            dGame["finished"] = True
            dScores["losses"] += 1
            dGame["message"] = "Game over! The word was " + sWord + "."
        elif is_correct(sWord, sLetter):
            dGame["message"] = "Good guess!"
        else:
            dGame["message"] = "Sorry, that letter is not in the word."

    display_round(dGame, dScores)
    return True


def main() -> None:
    """Load the game data and allow the player to play rounds.

    Args:
        None

    Returns:
        None.
    """
    try:
        dCategories: dict[str, list[str]] = load_categories()
    except FileNotFoundError:
        print("Cannot find words.txt. Run the game from its folder.")
        return

    if len(dCategories) == 0:
        print("No words were found in words.txt.")
        return

    dScores: dict[str, int] = load_scores()
    bPlaying: bool = True

    while bPlaying:
        sCategory: str
        sDifficulty: str
        sCategory, sDifficulty = choose_settings(dCategories)
        dGame: dict = new_round(dCategories, sCategory, sDifficulty)
        bCompleted: bool = play_round(dGame, dScores)

        if bCompleted:
            save_scores(dScores)

        sAnswer: str = input("\nPlay again? (Y/N): ").strip().upper()
        if sAnswer != "Y":
            bPlaying = False

    print("Thanks for playing!")


if __name__ == "__main__":
    main()

