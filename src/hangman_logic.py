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
    """Add a valid, previously unguessed letter to the list.

    Args:
        lGuesses (list[str]): List of previously guessed uppercase letters.
            Modified only when a valid, new letter is added.
        sLetter (str): A proposed single uppercase letter (A-Z).

    Returns:
        True if the letter was added; otherwise False.
    """

    bAdded: bool = False

    if (len(sLetter) == 1 and sLetter >= "A" and sLetter <= "Z"
        and sLetter not in lGuesses):
            lGuesses.append(sLetter)
            bAdded = True

    return bAdded


# 3. show_word
def show_word(sWord: str, lGuesses: list[str]) -> str:
    """Construct the word display using letters and underscores.

    Args:
        sWord (str): The uppercase secret word.
        lGuesses (list[str]): Previously guessed uppercase letters.
            This list is not modified.

    Returns:
        A string containing revealed letters and underscores for
        unguessed letters, separated by spaces.
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
    """Count guessed letters that do not occur in the secret word.

    Args:
        sWord (str): The uppercase secret word.
        lGuesses (list[str]): Previously guessed uppercase letters.
            This list is not modified.

    Returns:
        The number of incorrect guesses in lGuesses.
    """

    iMisses: int = 0

    for sLetter in lGuesses:
        if not is_correct(sWord, sLetter):
            iMisses += 1

    return iMisses


# 5. is_won
def is_won(sWord: str, lGuesses: list[str]) -> bool:
    """Determine whether every letter in the secret word has been guessed.

    Args:
        sWord (str): The uppercase secret word.
        lGuesses (list[str]): Previously guessed uppercase letters.
            This list is not modified.

    Returns:
        True if every letter in sWord appears in lGuesses;
        otherwise False.
    """

    bWon: bool = True

    for sLetter in sWord:
        if sLetter not in lGuesses:
            bWon = False

    return bWon


# 6. is_lost
def is_lost(sWord: str, lGuesses: list[str]) -> bool:
    """Determine whether the player has lost the round.

    Args:
        sWord (str): The uppercase secret word.
        lGuesses (list[str]): Previously guessed uppercase letters.
            This list is not modified.

    Returns:
        True if the number of incorrect guesses is greater than
        or equal to MAX_MISSES; otherwise False.
    """

    return count_misses(sWord, lGuesses) >= MAX_MISSES


# 7. calculate_score
def calculate_score(sWord: str, iMisses: int, sDifficulty: str) -> int:
    """Calculate points earned for winning a round.

    Args:
        sWord (str): The correctly guessed uppercase secret word.
        iMisses (int): Number of incorrect guesses, from 0 to MAX_MISSES.
        sDifficulty (str): The difficulty level: EASY, MEDIUM, or HARD.

    Returns:
        The score calculated as ten points per letter plus five
        points per remaining allowed miss, multiplied by the
        difficulty multiplier (1 for EASY, 2 for MEDIUM, 3 for HARD).
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
    """Select words of the appropriate length for a difficulty level.

    Args:
        lWords (list[str]): Uppercase words from one category.
            This list is not modified.
        sDifficulty (str): The difficulty level: EASY, MEDIUM, or HARD.

    Returns:
        A new list containing words with 4-5 letters for EASY,
        6-7 for MEDIUM, or 8-10 for HARD.
        Returns an empty list if no words match.
    """

    lSelected: list[str] = []

    for sWord in lWords:
        iLength: int = len(sWord)

        if ((sDifficulty == "EASY" and iLength >= 4 and iLength <= 5) or
            (sDifficulty == "MEDIUM" and iLength >= 6 and iLength <= 7) or
            (sDifficulty == "HARD" and iLength >= 8 and iLength <= 10)):
            lSelected.append(sWord)

    return lSelected


# 10. select_category
def select_category(
        dCategories: dict[str, list[str]], sCategory: str
    ) -> list[str]:
    """Find the words belonging to a selected category.

    Args:
        dCategories (dict[str, list[str]]): A dictionary mapping
            uppercase category names to lists of uppercase words.
        sCategory (str): The uppercase category name to find.

    Returns:
        The list of words belonging to the selected category,
        or an empty list if the category does not exist.
        The returned list is not a copy.
    """

    lWords: list[str] = []

    if sCategory in dCategories:
        lWords = dCategories[sCategory]

    return lWords


# 11. load_categories
def load_categories() -> dict[str, list[str]]:
    """Load words organized by category from words.txt.

    Returns:
        A dictionary mapping uppercase category names to lists
        of uppercase words. Each line in the file contains a
        category and word separated by a comma (CATEGORY,WORD).
        The input file is guaranteed to be correctly formatted.

    Raises:
        FileNotFoundError: If words.txt cannot be found.
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
    """Read cumulative scores from scores.txt.

    Returns:
        A dictionary containing integer values for wins, losses,
        and points. Each line in scores.txt has the format
        name,number. The file is guaranteed to be correctly formatted.
        If the file does not exist, all three values are zero.
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
        pass # dScores already initialized

    return dScores


# 13. save_scores
def save_scores(dScores: dict[str, int]) -> None:
    """Write cumulative scores to scores.txt.

    Args:
        dScores (dict[str, int]): A dictionary containing integer
            values for wins, losses, and points. Not modified.

    Returns:
        None. Creates scores.txt if it does not exist, or
        overwrites its contents if it already exists.
        Each line has the format name,number.
    """

    with open(SCORES_FILE, "w", encoding="utf-8") as oFile:
        for sName in dScores:
            oFile.write(sName + "," + str(dScores[sName]) + "\n")


# 14. new_round
def new_round(dCategories: dict[str, list[str]],
              sCategory: str, sDifficulty: str) -> dict:
    """Create and initialize the state for a new Hangman round.

    Args:
        dCategories (dict[str, list[str]]): Dictionary mapping uppercase
            category names to lists of uppercase words. Not modified.
        sCategory (str): The selected uppercase category name.
        sDifficulty (str): The difficulty level: EASY, MEDIUM, or HARD.

    Returns:
        A dictionary containing six keys:
            "word": A randomly selected word matching the category
                and difficulty.
            "guesses": An empty list.
            "finished": False.
            "message": The string "Choose a letter!"
            "category": The selected category.
            "difficulty": The selected difficulty.

    Raises:
        ValueError: If no words match the selected category
            and difficulty.
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


