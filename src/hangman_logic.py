"""Student Hangman logic: fourteen documented functions."""

import random

MAX_MISSES: int = 6
WORDS_FILE: str = "words.txt"
SCORES_FILE: str = "scores.txt"


# 1. is_correct
def is_correct(sWord: str, sLetter: str) -> bool:
    """Check whether a letter occurs in the secret word.

    Args:
        sWord (str): the uppercase secret word
        sLetter (str): the uppercase letter being guessed

    Returns:
        True if the letter appears in the word; otherwise False.
    """
    return sLetter in sWord


# 2. record_guess
def record_guess(lGuesses: list[str], sLetter: str) -> bool:
    """Add a valid, previously unguessed letter.

    Args:
        lGuesses (list[str]): letters already guessed
        sLetter (str): the proposed uppercase letter

    Returns:
        True if the letter was added; otherwise False.
    """
    bAdded: bool = False

    if len(sLetter) == 1 and sLetter >= "A" and sLetter <= "Z":
        if sLetter not in lGuesses:
            lGuesses.append(sLetter)
            bAdded = True

    return bAdded


# 3. show_word
def show_word(sWord: str, lGuesses: list[str]) -> str:
    """Construct the word display using letters and underscores.

    Args:
        sWord (str): the uppercase secret word
        lGuesses (list[str]): letters already guessed

    Returns:
        The revealed word with spaces between positions.
        For PYTHON with P and T guessed, return 'P _ T _ _ _'.
    """
    sDisplay: str = ""

    for iIndex in range(len(sWord)):
        if iIndex > 0:
            sDisplay += " "

        if sWord[iIndex] in lGuesses:
            sDisplay += sWord[iIndex]
        else:
            sDisplay += "_"

    return sDisplay


# 4. count_misses
def count_misses(sWord: str, lGuesses: list[str]) -> int:
    """Count guessed letters that do not occur in the word.

    Args:
        sWord (str): the uppercase secret word
        lGuesses (list[str]): letters already guessed

    Returns:
        The number of incorrect guesses.
    """
    iMisses: int = 0

    for sLetter in lGuesses:
        if not is_correct(sWord, sLetter):
            iMisses += 1

    return iMisses


# 5. is_won
def is_won(sWord: str, lGuesses: list[str]) -> bool:
    """Check whether every letter in the word has been guessed.

    Args:
        sWord (str): the uppercase secret word
        lGuesses (list[str]): letters already guessed

    Returns:
        True if all letters have been guessed; otherwise False.
    """
    bWon: bool = True

    for sLetter in sWord:
        if sLetter not in lGuesses:
            bWon = False

    return bWon


# 6. is_lost
def is_lost(sWord: str, lGuesses: list[str]) -> bool:
    """Check whether the player has reached the miss limit.

    Args:
        sWord (str): the uppercase secret word
        lGuesses (list[str]): letters already guessed

    Returns:
        True when incorrect guesses reach MAX_MISSES; otherwise False.
    """
    return count_misses(sWord, lGuesses) >= MAX_MISSES


# 7. calculate_score
def calculate_score(sWord: str, iMisses: int, sDifficulty: str) -> int:
    """Calculate points earned for winning a round.

    Args:
        sWord (str): the correctly guessed secret word
        iMisses (int): the number of incorrect guesses
        sDifficulty (str): EASY, MEDIUM, or HARD

    Returns:
        Ten points per letter plus five per remaining allowed miss,
        multiplied by 1 for EASY, 2 for MEDIUM, or 3 for HARD.
    """
    iMultiplier: int = 1

    if sDifficulty == "MEDIUM":
        iMultiplier = 2
    elif sDifficulty == "HARD":
        iMultiplier = 3

    iRemaining: int = MAX_MISSES - iMisses
    return (len(sWord) * 10 + iRemaining * 5) * iMultiplier


# 8. choose_word
def choose_word(lWords: list[str]) -> str:
    """Select a random word from a nonempty list.

    Args:
        lWords (list[str]): available uppercase words

    Returns:
        One randomly chosen word.
    """
    return random.choice(lWords)


# 9. get_words_by_difficulty
def get_words_by_difficulty(lWords: list[str], sDifficulty: str) -> list[str]:
    """Select words of the appropriate length.

    Args:
        lWords (list[str]): words from one category
        sDifficulty (str): EASY, MEDIUM, or HARD

    Returns:
        A list of words with 4-5 letters for EASY, 6-7 for MEDIUM,
        or 8-10 for HARD.
    """
    lSelected: list[str] = []

    for sWord in lWords:
        iLength: int = len(sWord)

        if sDifficulty == "EASY" and iLength >= 4 and iLength <= 5:
            lSelected.append(sWord)
        elif sDifficulty == "MEDIUM" and iLength >= 6 and iLength <= 7:
            lSelected.append(sWord)
        elif sDifficulty == "HARD" and iLength >= 8 and iLength <= 10:
            lSelected.append(sWord)

    return lSelected


# 10. select_category
def select_category(dCategories: dict[str, list[str]], sCategory: str) -> list[str]:
    """Find the words belonging to a category.

    Args:
        dCategories (dict[str, list[str]]): category names and word lists
        sCategory (str): the selected category

    Returns:
        The category's words, or an empty list if it does not exist.
    """
    lWords: list[str] = []

    if sCategory in dCategories:
        lWords = dCategories[sCategory]

    return lWords


# 11. load_categories
def load_categories() -> dict[str, list[str]]:
    """Load words organized by category from words.txt.

    Args:
        None

    Returns:
        A dictionary mapping categories to word lists.
        Each input line has the format CATEGORY,WORD.
    """
    dCategories: dict[str, list[str]] = {}

    with open(WORDS_FILE, "r", encoding="utf-8") as oFile:
        for sLine in oFile:
            sLine = sLine.strip()
            if sLine != "":
                lParts: list[str] = sLine.split(",")
                if len(lParts) == 2:
                    sCategory: str = lParts[0].strip().upper()
                    sWord: str = lParts[1].strip().upper()

                    if sCategory not in dCategories:
                        dCategories[sCategory] = []

                    dCategories[sCategory].append(sWord)

    return dCategories


# 12. load_scores
def load_scores() -> dict[str, int]:
    """Read the saved cumulative scores.

    Args:
        None

    Returns:
        A dictionary containing wins, losses, and points.
        If the score file is missing, all values are zero.
        Each line of the file has the format name,number.
    """
    dScores: dict[str, int] = {"wins": 0, "losses": 0, "points": 0}

    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as oFile:
            for sLine in oFile:
                lParts: list[str] = sLine.strip().split(",")
                if len(lParts) == 2:
                    sName: str = lParts[0].strip()
                    if sName in dScores:
                        dScores[sName] = int(lParts[1].strip())
    except FileNotFoundError:
        pass

    return dScores


# 13. save_scores
def save_scores(dScores: dict[str, int]) -> None:
    """Write cumulative scores to scores.txt.

    Args:
        dScores (dict[str, int]): wins, losses, and points

    Returns:
        None.
    """
    with open(SCORES_FILE, "w", encoding="utf-8") as oFile:
        for sName in dScores:
            oFile.write(sName + "," + str(dScores[sName]) + "\n")


# 14. new_round
def new_round(dCategories: dict[str, list[str]],
              sCategory: str, sDifficulty: str) -> dict:
    """Create the state for a new round.

    Args:
        dCategories (dict[str, list[str]]): all category word lists
        sCategory (str): the selected category
        sDifficulty (str): EASY, MEDIUM, or HARD

    Returns:
        A dictionary with word, guesses, finished, message,
        category, and difficulty. Raises ValueError if no words
        match the selected category and difficulty.
    """
    lWords: list[str] = select_category(dCategories, sCategory)
    lWords = get_words_by_difficulty(lWords, sDifficulty)

    if len(lWords) == 0:
        raise ValueError("No words match that category and difficulty.")

    dGame: dict = {}
    dGame["word"] = choose_word(lWords)
    dGame["guesses"] = []
    dGame["finished"] = False
    dGame["message"] = "Choose a letter!"
    dGame["category"] = sCategory
    dGame["difficulty"] = sDifficulty

    return dGame


