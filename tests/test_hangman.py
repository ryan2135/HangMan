
"""Instructor-supplied tests for the fourteen Hangman logic functions.

Run from the project root:
    python3 run_tests.py
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import hangman_logic as logic


class TestHangman(unittest.TestCase):
    """Test normal behavior, boundaries, and documented errors."""

    def test_01_is_correct(self) -> None:
        self.assertTrue(logic.is_correct("PYTHON", "P"))
        self.assertTrue(logic.is_correct("PYTHON", "T"))
        self.assertTrue(logic.is_correct("PYTHON", "N"))
        self.assertFalse(logic.is_correct("PYTHON", "A"))
        self.assertFalse(logic.is_correct("PYTHON", "Z"))

        # Repeated letters and single-letter words
        self.assertTrue(logic.is_correct("APPLE", "P"))
        self.assertTrue(logic.is_correct("BANANA", "A"))
        self.assertTrue(logic.is_correct("A", "A"))
        self.assertFalse(logic.is_correct("A", "B"))

        # Empty word
        self.assertFalse(logic.is_correct("", "A"))

    def test_02_record_guess(self) -> None:
        lGuesses: list[str] = []

        self.assertTrue(logic.record_guess(lGuesses, "P"))
        self.assertEqual(lGuesses, ["P"])

        self.assertTrue(logic.record_guess(lGuesses, "T"))
        self.assertEqual(lGuesses, ["P", "T"])

        # Duplicate guesses
        self.assertFalse(logic.record_guess(lGuesses, "P"))
        self.assertFalse(logic.record_guess(lGuesses, "T"))

        # Invalid guesses
        self.assertFalse(logic.record_guess(lGuesses, "12"))
        self.assertFalse(logic.record_guess(lGuesses, "p"))
        self.assertFalse(logic.record_guess(lGuesses, ""))
        self.assertFalse(logic.record_guess(lGuesses, "AB"))
        self.assertFalse(logic.record_guess(lGuesses, "1"))
        self.assertFalse(logic.record_guess(lGuesses, " "))
        self.assertFalse(logic.record_guess(lGuesses, "@"))

        # Alphabet boundaries
        self.assertTrue(logic.record_guess(lGuesses, "A"))
        self.assertTrue(logic.record_guess(lGuesses, "Z"))

        # Only valid, new guesses are stored
        self.assertEqual(lGuesses, ["P", "T", "A", "Z"])

    def test_03_show_word(self) -> None:
        self.assertEqual(
            logic.show_word("PYTHON", []),
            "_ _ _ _ _ _"
        )
        self.assertEqual(
            logic.show_word("PYTHON", ["P", "T"]),
            "P _ T _ _ _"
        )
        self.assertEqual(
            logic.show_word("PYTHON", ["A", "Z"]),
            "_ _ _ _ _ _"
        )
        self.assertEqual(
            logic.show_word("PYTHON", list("PYTHON")),
            "P Y T H O N"
        )

        # Repeated letters
        self.assertEqual(
            logic.show_word("APPLE", ["P"]),
            "_ P P _ _"
        )
        self.assertEqual(
            logic.show_word("BANANA", ["A"]),
            "_ A _ A _ A"
        )

        # Single-letter and empty words
        self.assertEqual(logic.show_word("A", []), "_")
        self.assertEqual(logic.show_word("A", ["A"]), "A")
        self.assertEqual(logic.show_word("", []), "")

    def test_04_count_misses(self) -> None:
        self.assertEqual(logic.count_misses("PYTHON", []), 0)
        self.assertEqual(
            logic.count_misses("PYTHON", ["P", "T"]), 0
        )
        self.assertEqual(
            logic.count_misses("PYTHON", ["A", "B", "C"]), 3
        )
        self.assertEqual(
            logic.count_misses("PYTHON", ["P", "A", "E", "T"]), 2
        )
        self.assertEqual(
            logic.count_misses(
                "PYTHON", ["A", "B", "C", "D", "E", "F"]
            ), 6
        )
        self.assertEqual(
            logic.count_misses("APPLE", ["P", "X", "L"]), 1
        )

        # A repeated incorrect guess is counted for each occurrence
        # if supplied directly in the list.
        self.assertEqual(
            logic.count_misses("BEAR", ["X", "X"]), 2
        )

    def test_05_is_won(self) -> None:
        self.assertFalse(logic.is_won("PYTHON", []))
        self.assertFalse(logic.is_won("PYTHON", ["P", "Y"]))
        self.assertFalse(
            logic.is_won("PYTHON", ["P", "Y", "T", "H", "O"])
        )
        self.assertTrue(
            logic.is_won("PYTHON", list("PYTHON"))
        )

        # Repeated letters need only one guess
        self.assertTrue(
            logic.is_won("APPLE", ["A", "P", "L", "E"])
        )

        # Extra incorrect guesses do not prevent a win
        self.assertTrue(
            logic.is_won("BEAR", ["B", "E", "A", "R", "X"])
        )

        self.assertFalse(logic.is_won("A", []))
        self.assertTrue(logic.is_won("A", ["A"]))

        # Every letter in an empty word is vacuously guessed
        self.assertTrue(logic.is_won("", []))

    def test_06_is_lost(self) -> None:
        self.assertFalse(logic.is_lost("PYTHON", []))
        self.assertFalse(logic.is_lost("PYTHON", ["P", "Y"]))
        self.assertFalse(logic.is_lost("PYTHON", ["A"]))

        # Immediately below the limit
        self.assertFalse(
            logic.is_lost(
                "PYTHON", ["A", "B", "C", "D", "E"]
            )
        )

        # Exactly at the limit
        self.assertTrue(
            logic.is_lost(
                "PYTHON", ["A", "B", "C", "D", "E", "F"]
            )
        )

        # Above the limit
        self.assertTrue(
            logic.is_lost(
                "PYTHON", ["A", "B", "C", "D", "E", "F", "G"]
            )
        )

        # Correct guesses do not count as misses
        self.assertFalse(
            logic.is_lost(
                "PYTHON", ["P", "Y", "A", "B", "C", "D", "E"]
            )
        )

    def test_07_calculate_score(self) -> None:
        # Formula:
        # (10 * word length + 5 * remaining misses) * multiplier
        # EASY = 1, MEDIUM = 2, HARD = 3

        # Original reference cases
        self.assertEqual(
            logic.calculate_score("BEAR", 0, "EASY"), 70
        )
        self.assertEqual(
            logic.calculate_score("MONKEY", 2, "MEDIUM"), 160
        )
        self.assertEqual(
            logic.calculate_score("ELEPHANT", 6, "HARD"), 240
        )

        # Different word, same length
        self.assertEqual(
            logic.calculate_score("WOLF", 0, "EASY"), 70
        )

        # Different word length
        self.assertEqual(
            logic.calculate_score("TIGER", 0, "EASY"), 80
        )

        # Miss boundaries
        self.assertEqual(
            logic.calculate_score("BEAR", 1, "EASY"), 65
        )
        self.assertEqual(
            logic.calculate_score("BEAR", 5, "EASY"), 45
        )
        self.assertEqual(
            logic.calculate_score("BEAR", 6, "EASY"), 40
        )

        # Multipliers
        self.assertEqual(
            logic.calculate_score("BEAR", 0, "MEDIUM"), 140
        )
        self.assertEqual(
            logic.calculate_score("BEAR", 0, "HARD"), 210
        )

    def test_08_choose_word(self) -> None:
        self.assertEqual(
            logic.choose_word(["PYTHON"]), "PYTHON"
        )

        lWords: list[str] = ["BEAR", "WOLF"]
        for _ in range(20):
            self.assertIn(logic.choose_word(lWords), lWords)

        lWords = [
            "BEAR", "WOLF", "TIGER", "MONKEY", "RABBIT"
        ]
        for _ in range(20):
            self.assertIn(logic.choose_word(lWords), lWords)

        # Input must remain unchanged
        self.assertEqual(
            lWords,
            ["BEAR", "WOLF", "TIGER", "MONKEY", "RABBIT"]
        )

        # random.choice raises IndexError for an empty list
        with self.assertRaises(IndexError):
            logic.choose_word([])

    def test_09_get_words_by_difficulty(self) -> None:
        lWords: list[str] = [
            "CAT",         # 3
            "BEAR",        # 4
            "TIGER",       # 5
            "MONKEY",      # 6
            "PANTHER",     # 7
            "ELEPHANT",    # 8
            "ALLIGATOR",   # 9
            "BASKETBALL",  # 10
            "ABCDEFGHIJK"  # 11
        ]

        # Test both boundaries of every difficulty
        self.assertEqual(
            logic.get_words_by_difficulty(lWords, "EASY"),
            ["BEAR", "TIGER"]
        )
        self.assertEqual(
            logic.get_words_by_difficulty(lWords, "MEDIUM"),
            ["MONKEY", "PANTHER"]
        )
        self.assertEqual(
            logic.get_words_by_difficulty(lWords, "HARD"),
            ["ELEPHANT", "ALLIGATOR", "BASKETBALL"]
        )

        # Empty input
        self.assertEqual(
            logic.get_words_by_difficulty([], "EASY"), []
        )

        # No matching words
        self.assertEqual(
            logic.get_words_by_difficulty(["BEAR"], "HARD"),
            []
        )

        # Unknown difficulty
        self.assertEqual(
            logic.get_words_by_difficulty(lWords, "UNKNOWN"),
            []
        )

    def test_10_select_category(self) -> None:
        dCategories: dict[str, list[str]] = {
            "ANIMALS": ["BEAR", "TIGER"],
            "SPORTS": ["GOLF"],
            "SCIENCE": []
        }

        self.assertEqual(
            logic.select_category(dCategories, "ANIMALS"),
            ["BEAR", "TIGER"]
        )
        self.assertEqual(
            logic.select_category(dCategories, "SPORTS"),
            ["GOLF"]
        )
        self.assertEqual(
            logic.select_category(dCategories, "SCIENCE"),
            []
        )
        self.assertEqual(
            logic.select_category(dCategories, "UNKNOWN"),
            []
        )
        self.assertEqual(
            logic.select_category({}, "ANIMALS"),
            []
        )

        # Category lookup is case-sensitive
        self.assertEqual(
            logic.select_category(dCategories, "animals"),
            []
        )

    def test_11_load_categories(self) -> None:
        import os

        sOriginalFolder: str = os.getcwd()

        with tempfile.TemporaryDirectory() as sFolder:
            try:
                os.chdir(sFolder)
                oFile: Path = Path("words.txt")

                # Multiple categories
                oFile.write_text(
                    "ANIMALS,BEAR\n"
                    "SPORTS,GOLF\n"
                    "ANIMALS,TIGER\n"
                    "SCIENCE,ATOM\n"
                    "SPORTS,TENNIS\n",
                    encoding="utf-8"
                )

                self.assertEqual(
                    logic.load_categories(),
                    {
                        "ANIMALS": ["BEAR", "TIGER"],
                        "SPORTS": ["GOLF", "TENNIS"],
                        "SCIENCE": ["ATOM"]
                    }
                )

                # Single record
                oFile.write_text("ANIMALS,BEAR\n", encoding="utf-8")
                self.assertEqual(
                    logic.load_categories(),
                    {"ANIMALS": ["BEAR"]}
                )

                # Empty file
                oFile.write_text("", encoding="utf-8")
                self.assertEqual(logic.load_categories(), {})

                # Missing file
                oFile.unlink()
                with self.assertRaises(FileNotFoundError):
                    logic.load_categories()

            finally:
                os.chdir(sOriginalFolder)

    def test_12_load_scores(self) -> None:
        import os

        sOriginalFolder: str = os.getcwd()

        with tempfile.TemporaryDirectory() as sFolder:
            try:
                os.chdir(sFolder)
                oFile: Path = Path("scores.txt")

                # Missing file
                self.assertEqual(
                    logic.load_scores(),
                    {"wins": 0, "losses": 0, "points": 0}
                )

                # Existing file
                oFile.write_text(
                    "wins,3\n"
                    "losses,2\n"
                    "points,145\n",
                    encoding="utf-8"
                )

                self.assertEqual(
                    logic.load_scores(),
                    {"wins": 3, "losses": 2, "points": 145}
                )

            finally:
                os.chdir(sOriginalFolder)

    def test_13_save_scores(self) -> None:
        import os

        sOriginalFolder: str = os.getcwd()

        with tempfile.TemporaryDirectory() as sFolder:
            try:
                os.chdir(sFolder)
                oFile: Path = Path("scores.txt")

                # Create a new file
                dScores: dict[str, int] = {
                    "wins": 3,
                    "losses": 2,
                    "points": 145
                }
                logic.save_scores(dScores)

                self.assertEqual(
                    oFile.read_text(encoding="utf-8"),
                    "wins,3\nlosses,2\npoints,145\n"
                )

                # # Overwrite existing file
                # dScores = {
                #     "wins": 10,
                #     "losses": 5,
                #     "points": 1000
                # }
                # logic.save_scores(dScores)

                # self.assertEqual(
                #     oFile.read_text(encoding="utf-8"),
                #     "wins,10\nlosses,5\npoints,1000\n"
                # )

                # # Save zero scores
                # dScores = {
                #     "wins": 0,
                #     "losses": 0,
                #     "points": 0
                # }
                # logic.save_scores(dScores)

                # self.assertEqual(
                #     oFile.read_text(encoding="utf-8"),
                #     "wins,0\nlosses,0\npoints,0\n"
                # )

            finally:
                os.chdir(sOriginalFolder)

    def test_14_new_round(self) -> None:
        dCategories: dict[str, list[str]] = {
            "ANIMALS": [
                "BEAR",
                "MONKEY",
                "ELEPHANT"
            ]
        }

        # Easy round
        dGame: dict = logic.new_round(
            dCategories, "ANIMALS", "EASY"
        )
        self.assertEqual(dGame["word"], "BEAR")
        self.assertEqual(dGame["guesses"], [])
        self.assertFalse(dGame["finished"])
        self.assertEqual(dGame["message"], "Choose a letter!")
        self.assertEqual(dGame["category"], "ANIMALS")
        self.assertEqual(dGame["difficulty"], "EASY")

        # Medium round
        dGame = logic.new_round(
            dCategories, "ANIMALS", "MEDIUM"
        )
        self.assertEqual(dGame["word"], "MONKEY")
        self.assertEqual(dGame["guesses"], [])
        self.assertFalse(dGame["finished"])
        self.assertEqual(dGame["difficulty"], "MEDIUM")

        # Hard round
        dGame = logic.new_round(
            dCategories, "ANIMALS", "HARD"
        )
        self.assertEqual(dGame["word"], "ELEPHANT")
        self.assertEqual(dGame["guesses"], [])
        self.assertFalse(dGame["finished"])
        self.assertEqual(dGame["difficulty"], "HARD")

        # Invalid category
        with self.assertRaises(ValueError):
            logic.new_round(
                dCategories, "UNKNOWN", "EASY"
            )

        # No matching words for difficulty
        with self.assertRaises(ValueError):
            logic.new_round(
                {"ANIMALS": ["BEAR"]},
                "ANIMALS",
                "HARD"
            )

        # Empty categories
        with self.assertRaises(ValueError):
            logic.new_round({}, "ANIMALS", "EASY")


if __name__ == "__main__":
    unittest.main()
