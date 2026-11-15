import os
from pathlib import Path

TEXT_GAME: str = "1"
GRAPHICAL_GAME: str = "2"


def main() -> None:
    os.chdir(Path(__file__).resolve().parent)

    print("HANGMAN")
    print(f"{TEXT_GAME}. Text version")
    print(f"{GRAPHICAL_GAME}. Graphical version")

    sChoice: str = input("Choose an option: ")

    if sChoice == TEXT_GAME:
        from hangman_text import main as text_main
        text_main()
    elif sChoice == GRAPHICAL_GAME:
        from hangman_graphics import main as graphics_main
        graphics_main()
    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()
