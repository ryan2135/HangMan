import os
from pathlib import Path


def main() -> None:
    os.chdir(Path(__file__).resolve().parent)

    print("HANGMAN")
    print("1. Text version")
    print("2. Graphical version")

    sChoice: str = input("Choose an option: ")

    if sChoice == "1":
        from hangman_text import main as text_main
        text_main()
    elif sChoice == "2":
        from hangman_graphics import main as graphics_main
        graphics_main()
    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()