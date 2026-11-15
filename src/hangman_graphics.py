"""Graphical Hangman interface using the shared student logic functions.

STUDENT READING GUIDE
---------------------
This file is supplied. You do not need to understand Pygame to complete
Hangman. If you are curious, follow the sections below to see how your
14 functions connect to a graphical application.

The game logic lives in hangman_logic.py; this file only displays the game,
collects player input, and calls those functions.
"""

import pygame

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

# 1. APPEARANCE: Screen dimensions and RGB color constants.
# Colors are (red, green, blue), with each component from 0 to 255.
WIDTH, HEIGHT = 1000, 700
NAVY = (25, 42, 65)
BLUE = (47, 87, 133)
PALE = (235, 245, 249)
WHITE = (255, 255, 255)
GREEN = (39, 145, 111)
RED = (197, 76, 85)
INK = (34, 53, 73)
GOLD = (250, 201, 110)
GRAY = (198, 211, 218)


# ============================================================
# 2. DRAWING HELPERS
# Pygame draws shapes and text on a Surface (the game window).
# These functions are supplied; students do not need to modify them.
# ============================================================


def rounded(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    rect: pygame.Rect,
    radius: int = 14,
) -> None:
    """Draw a rounded rectangle.

    Args:
        surface (pygame.Surface): destination window
        color (tuple[int, int, int]): RGB fill color
        rect (pygame.Rect): position and size
        radius (int): corner radius

    Returns:
        None.
    """
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_text(
    surface: pygame.Surface,
    value: str,
    size: int,
    color: tuple[int, int, int],
    center: tuple[int, int],
    bold: bool = False,
) -> None:
    """Draw centered text on the window.

    Args:
        surface (pygame.Surface): destination window
        value (str): text to draw
        size (int): font size
        color (tuple[int, int, int]): RGB text color
        center (tuple[int, int]): text center coordinates
        bold (bool): whether to use bold text

    Returns:
        None.
    """
    font = pygame.font.SysFont("dejavusans", size, bold=bold)
    image = font.render(value, True, color)
    surface.blit(image, image.get_rect(center=center))


def draw_background(surface: pygame.Surface) -> None:
    """Draw the landscape and title.

    Args:
        surface (pygame.Surface): destination window

    Returns:
        None.
    """
    surface.fill((186, 225, 241))
    pygame.draw.circle(surface, GOLD, (852, 177), 65)
    pygame.draw.polygon(
        surface, (132, 173, 193), [(0, 405), (190, 190), (400, 405)]
    )
    pygame.draw.polygon(
        surface, (104, 148, 176), [(230, 405), (505, 175), (790, 405)]
    )
    pygame.draw.polygon(
        surface, (147, 186, 184), [(570, 405), (800, 230), (1000, 405)]
    )
    pygame.draw.rect(surface, (125, 175, 144), (0, 410, WIDTH, HEIGHT - 410))
    for x, y, s in [
        (25, 420, 1.0),
        (115, 470, 0.8),
        (900, 430, 1.1),
        (960, 510, 0.8),
    ]:
        pygame.draw.rect(surface, (96, 108, 86), (x - 6, y - 10, 12, 75))
        for level in range(3):
            cy = y - 30 - level * 27
            pygame.draw.polygon(
                surface,
                (43, 110, 91),
                [(x, cy - 70), (x - 40 * s, cy + 20), (x + 40 * s, cy + 20)],
            )
    rounded(surface, NAVY, pygame.Rect(0, 0, WIDTH, 100), 0)
    draw_text(surface, "H A N G M A N", 43, WHITE, (WIDTH // 2, 48), True)


# Each incorrect guess adds one body part; the miss count comes from
# the student's count_misses() function.
def draw_gallows(surface: pygame.Surface, misses: int) -> None:
    """Draw the gallows and body parts for the miss count.

    Args:
        surface (pygame.Surface): destination window
        misses (int): number of incorrect guesses

    Returns:
        None.
    """
    color = (95, 64, 42)
    pygame.draw.line(surface, color, (92, 440), (285, 440), 13)
    pygame.draw.line(surface, color, (145, 440), (145, 172), 13)
    pygame.draw.line(surface, color, (140, 175), (295, 175), 13)
    pygame.draw.line(surface, color, (290, 175), (290, 217), 5)
    figure = INK
    if misses >= 1:
        pygame.draw.circle(surface, figure, (290, 246), 27, 5)
    if misses >= 2:
        pygame.draw.line(surface, figure, (290, 273), (290, 352), 5)
    if misses >= 3:
        pygame.draw.line(surface, figure, (290, 295), (247, 330), 5)
    if misses >= 4:
        pygame.draw.line(surface, figure, (290, 295), (333, 330), 5)
    if misses >= 5:
        pygame.draw.line(surface, figure, (290, 352), (251, 401), 5)
    if misses >= 6:
        pygame.draw.line(surface, figure, (290, 352), (329, 401), 5)


# 3. INPUT CONTROLS: Build the on-screen alphabet and draw buttons.
# A pygame.Rect stores a button's position and size for mouse clicks.
def letter_buttons() -> dict[str, pygame.Rect]:
    """Create clickable rectangles for alphabet letters.

    Args:
        None

    Returns:
        A dictionary mapping each letter to its screen rectangle.
    """
    buttons: dict[str, pygame.Rect] = {}
    for index, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        row, col = divmod(index, 9)
        if row == 2:
            x = 478 + col * 55
        else:
            x = 455 + col * 55
        buttons[letter] = pygame.Rect(x, 438 + row * 58, 47, 48)
    return buttons


def draw_button(
    surface: pygame.Surface,
    label: str,
    rect: pygame.Rect,
    color: tuple[int, int, int],
    font_size: int = 23,
) -> None:
    """Draw a labeled button.

    Args:
        surface (pygame.Surface): destination window
        label (str): button text
        rect (pygame.Rect): button location and dimensions
        color (tuple[int, int, int]): RGB fill color
        font_size (int): text size

    Returns:
        None.
    """
    rounded(surface, (69, 92, 108), rect.move(0, 3), 11)
    rounded(surface, color, rect, 11)
    draw_text(
        surface,
        label,
        font_size,
        WHITE if color in (GREEN, RED, BLUE) else INK,
        rect.center,
        True,
    )


# 4. GAME DISPLAY: Turn the student's game-state dictionary into a screen.
# Notice the calls to count_misses(), show_word(), and is_correct().
def draw_game(
    surface: pygame.Surface,
    game: dict,
    scores: dict[str, int],
    buttons: dict[str, pygame.Rect],
    actions: dict[str, pygame.Rect],
) -> None:
    """Draw the game board, guesses, letters, and score totals.

    Args:
        surface (pygame.Surface): destination window
        game (dict): current round information
        scores (dict[str, int]): cumulative score totals
        buttons (dict[str, pygame.Rect]): alphabet button locations
        actions (dict[str, pygame.Rect]): action button locations

    Returns:
        None.
    """
    draw_background(surface)
    misses = count_misses(game["word"], game["guesses"])
    if misses is None:
        misses = 0
    draw_gallows(surface, misses)
    rounded(surface, (91, 128, 142), pygame.Rect(423, 151, 530, 185), 22)
    rounded(surface, WHITE, pygame.Rect(420, 145, 530, 185), 22)
    word_display = show_word(game["word"], game["guesses"])
    if word_display is None:
        word_display = "_ " * len(game["word"])
    draw_text(surface, word_display, 45, INK, (685, 222), True)
    draw_text(
        surface,
        f"Incorrect guesses: {misses} of {MAX_MISSES}",
        23,
        INK,
        (690, 302),
        True,
    )
    draw_text(
        surface,
        f"{game['category'].title()}  |  {game['difficulty'].title()}",
        19,
        INK,
        (685, 348),
        True,
    )
    rounded(surface, PALE, pygame.Rect(432, 365, 510, 50), 15)
    draw_text(surface, game["message"], 20, INK, (685, 391), True)
    for letter, rect in buttons.items():
        color = WHITE
        if letter in game["guesses"]:
            correct = is_correct(game["word"], letter)
            if correct:
                color = GREEN
            else:
                color = RED
        draw_button(surface, letter, rect, color)
    for label, rect in actions.items():
        draw_button(surface, label, rect, BLUE, 21)
    rounded(surface, WHITE, pygame.Rect(18, 603, 395, 65), 15)
    draw_text(
        surface,
        (
            f"Wins: {scores['wins']}   "
            f"Losses: {scores['losses']}   "
            f"Points: {scores['points']}"
        ),
        18,
        NAVY,
        (215, 637),
        True,
)
    draw_text(
        surface, "Click letters or use your keyboard", 16, NAVY, (705, 670)
    )


# 5. GAME SETTINGS: The player chooses a category and difficulty.
# The student functions filter the words before Play is enabled.
def choose_settings(
    screen: pygame.Surface,
    categories: dict[str, list[str]],
    current_category: str,
    current_difficulty: str,
) -> tuple[str, str] | None:
    """Display category and difficulty choices.

    Args:
        screen (pygame.Surface): the game window
        categories (dict[str, list[str]]): available word categories
        current_category (str): initially selected category
        current_difficulty (str): initially selected difficulty

    Returns:
        The selected category and difficulty, or None if the window closes.
    """
    category_names = sorted(categories)
    difficulties = ["EASY", "MEDIUM", "HARD"]
    category = current_category
    difficulty = current_difficulty
    clock = pygame.time.Clock()
    while True:
        draw_background(screen)
        rounded(screen, (91, 128, 142), pygame.Rect(200, 131, 610, 500), 20)
        rounded(screen, WHITE, pygame.Rect(195, 125, 610, 500), 20)
        draw_text(screen, "Choose your game", 32, NAVY, (500, 175), True)
        draw_text(screen, "Category", 24, INK, (500, 220), True)
        category_buttons: dict[str, pygame.Rect] = {}
        for i, name in enumerate(category_names):
            rect = pygame.Rect(
                260 + (i % 2) * 250, 250 + (i // 2) * 55, 230, 44
            )
            category_buttons[name] = rect
            draw_button(
                screen,
                name.title(),
                rect,
                GREEN if name == category else BLUE,
                19,
            )
        draw_text(
            screen, "Difficulty (by word length)", 23, INK, (500, 382), True
        )
        difficulty_buttons: dict[str, pygame.Rect] = {}
        for i, name in enumerate(difficulties):
            rect = pygame.Rect(250 + i * 172, 414, 155, 48)
            difficulty_buttons[name] = rect
            draw_button(
                screen,
                name.title(),
                rect,
                GREEN if name == difficulty else BLUE,
                19,
            )
        category_words = select_category(categories, category)
        possible_words = get_words_by_difficulty(category_words, difficulty)
        valid = possible_words is not None and len(possible_words) > 0
        draw_text(
            screen,
            "Ready to play" if valid else "No words for this combination",
            18,
            GREEN if valid else RED,
            (500, 493),
        )
        play_rect = pygame.Rect(390, 525, 220, 55)
        draw_button(screen, "Play", play_rect, GREEN if valid else GRAY, 24)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, rect in category_buttons.items():
                    if rect.collidepoint(event.pos):
                        category = name
                for name, rect in difficulty_buttons.items():
                    if rect.collidepoint(event.pos):
                        difficulty = name
                if play_rect.collidepoint(event.pos) and valid:
                    return category, difficulty
        clock.tick(30)


# 6. GAME LOOP: Initialize the window, listen for input, and redraw.
# This is where the two layers meet: Pygame handles the interface,
# while the 14 student functions handle the rules and saved scores.
def main() -> None:
    """Run the provided game window and dispatch student logic.

    Args:
        None

    Returns:
        None.
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hangman - CS170")
    clock = pygame.time.Clock()
    categories: dict[str, list[str]] = load_categories()
    scores: dict[str, int] = load_scores()
    category: str = next(iter(categories), "")
    difficulty: str = "EASY"
    if not categories:
        pygame.quit()
        print("No word categories found.")
        return

    selection = choose_settings(screen, categories, category, difficulty)
    if selection is None:
        pygame.quit()
        return
    category, difficulty = selection
    game: dict = new_round(categories, category, difficulty)
    buttons = letter_buttons()
    actions = {
        "New Game": pygame.Rect(440, 617, 155, 44),
        "Quit": pygame.Rect(815, 617, 125, 44),
    }
    running: bool = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if actions["Quit"].collidepoint(event.pos):
                    running = False
                elif actions["New Game"].collidepoint(event.pos):
                    loaded = load_categories()
                    if loaded is not None and len(loaded) > 0:
                        selection = choose_settings(
                            screen, loaded, category, difficulty
                        )
                        if selection is not None:
                            categories = loaded
                            category = selection[0]
                            difficulty = selection[1]
                            game = new_round(categories, category, difficulty)
                            loaded_scores = load_scores()
                            if loaded_scores is not None:
                                scores = loaded_scores
            letter: str = ""
            if event.type == pygame.KEYDOWN:
                letter = event.unicode.upper()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for candidate in buttons:
                    if buttons[candidate].collidepoint(event.pos):
                        letter = candidate
            # Pass the player's letter to student logic, then check for
            # a win or loss and save updated scores if the round ends.
            if not game["finished"] and letter != "":
                added = record_guess(game["guesses"], letter)
                if added:
                    won = is_won(game["word"], game["guesses"])
                    lost = is_lost(game["word"], game["guesses"])
                    if won:
                        game["finished"] = True
                        misses = count_misses(game["word"], game["guesses"])
                        points = calculate_score(
                            game["word"], misses, difficulty
                        )
                        if points is None:
                            points = 0
                        game["message"] = "You won! +" + str(points) + " points"
                        scores["wins"] = scores["wins"] + 1
                        scores["points"] = scores["points"] + points
                        save_scores(scores)
                    elif lost:
                        game["finished"] = True
                        game["message"] = "Game over! Word: " + game["word"]
                        scores["losses"] = scores["losses"] + 1
                        save_scores(scores)
                    elif is_correct(game["word"], letter):
                        game["message"] = "Nice guess!"
                    else:
                        game["message"] = "Try another letter."
        # Refresh the display every frame; the game state stays in game.
        draw_game(screen, game, scores, buttons, actions)
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()


if __name__ == "__main__":
    main()
