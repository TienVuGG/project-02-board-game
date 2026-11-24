"""Interactive Connect Four application for the Project 02 final milestone."""
from __future__ import annotations

import json
import math
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from game_engine import (  # noqa: E402
    COLUMNS,
    ROWS,
    PLAYER_O,
    PLAYER_X,
    GameState,
    board_from_rows,
    legal_moves,
)
from student_core import alphabeta, evaluate, reset_node_counters  # noqa: E402
import game_engine as game_engine_module
import student_core as student_core_module

try:
    import pygame
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "pygame is required to run this app. Install it with "
        "`pip install -r requirements.txt`."
    ) from exc


BOARD_CELL = 82
BOARD_LEFT = 24
BOARD_TOP = 74
SIDEBAR_LEFT = BOARD_LEFT + COLUMNS * BOARD_CELL + 28
SIDEBAR_WIDTH = 470
WIDTH = SIDEBAR_LEFT + SIDEBAR_WIDTH + 28
HEIGHT = BOARD_TOP + ROWS * BOARD_CELL + 28
RADIUS = BOARD_CELL // 2 - 9

COLOR_BG = (10, 15, 29)
COLOR_PANEL = (20, 29, 48)
COLOR_PANEL_EDGE = (42, 56, 82)
COLOR_BOARD = (31, 45, 70)
COLOR_EMPTY = (8, 14, 28)
COLOR_X = (56, 189, 248)
COLOR_O = (251, 146, 60)
COLOR_TEXT = (241, 245, 249)
COLOR_MUTED = (203, 213, 225)
COLOR_ACCENT = (129, 140, 248)
COLOR_ACCENT_HOVER = (165, 180, 252)
COLOR_DANGER = (251, 113, 133)
COLOR_GOOD = (74, 222, 128)

HUMAN = PLAYER_X
AI = PLAYER_O

MENU_WIDTH = 1280
MENU_HEIGHT = 720
MENU_BG = (35, 36, 111)
MENU_PANEL = (91, 91, 222)
MENU_YELLOW = (255, 197, 27)
MENU_RED = (210, 49, 43)
MENU_BORDER = (99, 122, 255)

GAME_WIDTH = 1280
GAME_HEIGHT = 660
GAME_CELL = 76
GAME_BOARD_TOP = 52
_PIECE_COLOR_CACHE: dict[int, tuple[object, tuple[int, int, int]]] = {}


def load_benchmarks() -> list[dict]:
    candidates = [Path(__file__).with_name("sample_states.json")]
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        candidates.extend(
            [
                Path(bundle_root) / "starter" / "sample_states.json",
                Path(bundle_root) / "sample_states.json",
            ]
        )
    for path in candidates:
        if path.is_file():
            with path.open(encoding="utf-8") as handle:
                return json.load(handle)["states"]
    searched = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Could not locate sample_states.json. Searched: {searched}")


def load_window_icon() -> pygame.Surface:
    candidates = [Path(__file__).resolve().parent.parent / "images.png"]
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        candidates.append(Path(bundle_root) / "images.png")
    for path in candidates:
        if path.is_file():
            return pygame.image.load(str(path))
    searched = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Could not locate images.png. Searched: {searched}")


def load_piece_library() -> dict[str, object]:
    roots = [Path(__file__).resolve().parent.parent / "assets"]
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        roots.extend([Path(bundle_root) / "assets", Path(bundle_root) / "starter" / "assets"])

    assets = {}
    for root in roots:
        if root.is_dir():
            for path in sorted(root.glob("*.png")):
                image = pygame.image.load(path).convert_alpha()
                content = image.get_bounding_rect(min_alpha=1)
                if content.width and content.height:
                    image = image.subsurface(content).copy()
                assets.setdefault(path.name, image)
    return assets


def default_piece_pair(piece_library: dict[str, object]) -> tuple[object | None, object | None]:
    available = list(piece_library.values())
    player = piece_library.get("huy-hieu-xanh-lam.png") or piece_library.get("player_piece.png")
    computer = piece_library.get("huy-hieu-ho-phach.png") or piece_library.get("computer_piece.png")
    if player is None and available:
        player = next((piece for piece in available if piece is not computer), available[0])
    if computer is None and available:
        computer = next((piece for piece in available if piece is not player), available[0])
    return player, computer


def benchmark_state(item: dict) -> GameState:
    """Convert one benchmark record into a validated runtime game state."""
    required = {"id", "board", "to_move", "description"}
    missing = required - item.keys()
    if missing:
        raise ValueError(f"Benchmark is missing fields: {sorted(missing)}")
    if item["to_move"] not in (PLAYER_X, PLAYER_O):
        raise ValueError(f"Invalid benchmark player: {item['to_move']!r}")
    game_engine_module.set_board_config(ROWS, COLUMNS, 4)
    student_core_module.set_ai_board_config(ROWS, COLUMNS, 4)
    return GameState(board_from_rows(item["board"]), item["to_move"])


def clamp_depth(value: int) -> int:
    """Normalize UI depth input to the supported integer range 1..7."""
    return max(1, min(7, int(value)))


def set_search_depth(value: int) -> int:
    """Return the product search depth after enforcing the 1..7 contract."""
    return clamp_depth(value)


def piece_color(token: str) -> tuple[int, int, int]:
    return COLOR_X if token == PLAYER_X else COLOR_O if token == PLAYER_O else COLOR_EMPTY


def piece_accent_color(asset, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
    if asset is None:
        return fallback
    cached = _PIECE_COLOR_CACHE.get(id(asset))
    if cached is not None and cached[0] is asset:
        return cached[1]

    sample = pygame.transform.smoothscale(asset, (24, 24))
    colors: dict[tuple[int, int, int], int] = {}
    for y in range(sample.get_height()):
        for x in range(sample.get_width()):
            red, green, blue, alpha = sample.get_at((x, y))
            channels = (red, green, blue)
            if alpha < 80 or max(channels) - min(channels) < 48 or max(channels) < 80:
                continue
            color = tuple(channel // 16 * 16 + 8 for channel in channels)
            colors[color] = colors.get(color, 0) + 1
    accent = max(colors, key=colors.get) if colors else fallback
    _PIECE_COLOR_CACHE[id(asset)] = (asset, accent)
    return accent


def random_piece_pair(available_pieces: list[object]) -> tuple[object | None, object | None]:
    if not available_pieces:
        return None, None
    if len(available_pieces) == 1:
        return available_pieces[0], available_pieces[0]
    player, computer = random.sample(available_pieces, 2)
    return player, computer


def evaluation_fraction(score: float) -> float:
    """Map an unbounded X-perspective score to the bar interval [0, 1]."""
    if score == 0:
        return 0.5
    return max(0.0, min(1.0, 0.5 + 0.5 * (score / (abs(score) + 250.0))))


def evaluation_label(score: float) -> str:
    """Return a concise label for the X-perspective board evaluation."""
    if score == 0:
        return "even"
    return f"{'X' if score > 0 else 'O'} {abs(score):.0f}"


def draw_text(screen, font, text: str, position, color=COLOR_TEXT) -> None:
    screen.blit(font.render(text, True, color), position)


def button(screen, font, label: str, rect, active: bool = False) -> bool:
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    fill = (99, 102, 241) if active else (37, 50, 76)
    if hovered and not active:
        fill = (55, 72, 108)
    pygame.draw.rect(screen, fill, rect, border_radius=8)
    if active:
        pygame.draw.rect(screen, COLOR_ACCENT_HOVER, rect, 1, border_radius=8)
    label_surface = font.render(label, True, COLOR_TEXT)
    label_x = rect.x + (rect.width - label_surface.get_width()) // 2
    label_y = rect.y + (rect.height - label_surface.get_height()) // 2
    screen.blit(label_surface, (label_x, label_y))
    return rect.collidepoint(pygame.mouse.get_pos())


def draw_board(screen, state: GameState) -> None:
    board_rect = pygame.Rect(
        BOARD_LEFT,
        BOARD_TOP,
        COLUMNS * BOARD_CELL,
        ROWS * BOARD_CELL,
    )
    pygame.draw.rect(screen, (5, 9, 20), board_rect.move(0, 6), border_radius=14)
    pygame.draw.rect(
        screen,
        COLOR_BOARD,
        board_rect,
        border_radius=14,
    )
    pygame.draw.rect(screen, COLOR_PANEL_EDGE, board_rect, 1, border_radius=14)
    for row in range(ROWS):
        for col in range(COLUMNS):
            center = (
                BOARD_LEFT + col * BOARD_CELL + BOARD_CELL // 2,
                BOARD_TOP + row * BOARD_CELL + BOARD_CELL // 2,
            )
            pygame.draw.circle(screen, piece_color(state.board[row][col]), center, RADIUS)
            pygame.draw.circle(screen, COLOR_MUTED, center, RADIUS, 1)


def draw_evaluation(screen, fonts, board) -> None:
    label_font, small_font = fonts
    raw = evaluate(board, PLAYER_X)
    normalized = evaluation_fraction(raw)
    x = SIDEBAR_LEFT
    y = 286
    width = 300
    pygame.draw.rect(screen, COLOR_EMPTY, (x, y, width, 22), border_radius=5)
    pygame.draw.rect(screen, COLOR_X, (x, y, int(width * normalized), 22), border_radius=5)
    draw_text(screen, label_font, "Board advantage", (x, y - 28))
    draw_text(screen, small_font, "X", (x - 18, y + 2), COLOR_X)
    draw_text(screen, small_font, "O", (x + width + 8, y + 2), COLOR_O)
    draw_text(screen, small_font, evaluation_label(raw), (x + 126, y + 27), COLOR_MUTED)


def draw_gear(screen, center, radius: int) -> pygame.Rect:
    x, y = center
    rect = pygame.Rect(x - 38, y - 38, 76, 76)
    scale = 1.12 if rect.collidepoint(pygame.mouse.get_pos()) else 1.0
    scaled_radius = int(38 * scale)
    pygame.draw.circle(screen, (99, 112, 255), center, scaled_radius)
    pygame.draw.circle(screen, (62, 69, 165), center, int(31 * scale))
    inner_radius = int(radius * scale)
    pygame.draw.circle(screen, (238, 242, 255), center, inner_radius)
    pygame.draw.circle(screen, (62, 69, 165), center, max(1, inner_radius - 7))
    for angle in range(0, 360, 45):
        radians = math.radians(angle)
        dx = int(9 * scale * math.cos(radians))
        dy = int(9 * scale * math.sin(radians))
        pygame.draw.circle(screen, (238, 242, 255), (x + dx, y + dy), 5)
    return rect


def draw_menu(
    screen,
    title_font,
    button_font,
    small_font,
    custom_selected: bool = False,
) -> tuple[pygame.Rect, pygame.Rect]:
    screen.fill(MENU_BG)

    title = title_font.render("CONNECT FOUR", True, (248, 249, 255))
    title_y = 78
    title_rect = title.get_rect(center=(MENU_WIDTH // 2, title_y))
    screen.blit(title, title_rect)

    ribbon_font = pygame.font.SysFont("segoeui", 30, bold=True)
    ribbon = ribbon_font.render("PLAY", True, (12, 14, 35))
    ribbon_rect = ribbon.get_rect(center=(MENU_WIDTH // 2 - 48, title_y - 43))
    ribbon_back = pygame.Rect(ribbon_rect.x - 18, ribbon_rect.y - 7, ribbon_rect.width + 36, ribbon_rect.height + 14)
    pygame.draw.rect(screen, MENU_RED, ribbon_back)
    pygame.draw.polygon(
        screen,
        MENU_RED,
        [
            (ribbon_back.right - 8, ribbon_back.top),
            (ribbon_back.right + 28, ribbon_back.top - 7),
            (ribbon_back.right - 2, ribbon_back.bottom),
        ],
    )
    screen.blit(ribbon, ribbon_rect)

    preview = pygame.Rect(MENU_WIDTH // 2 - 300, 205, 600, 174)
    pygame.draw.rect(screen, (79, 82, 183), preview, border_radius=18)
    preview_y = preview.y + preview.height // 2
    for index in range(4):
        cx = preview.x + 98 + index * 130
        color = MENU_RED if index == 3 else MENU_YELLOW
        pygame.draw.circle(screen, color, (cx, preview_y), 52)
        pygame.draw.circle(screen, (255, 255, 255), (cx, preview_y), 52, 2)
        pygame.draw.circle(screen, color, (cx, preview_y), 40)

    classic_rect = pygame.Rect(MENU_WIDTH // 2 - 265, 500, 250, 100)
    custom_rect = pygame.Rect(MENU_WIDTH // 2 + 15, 500, 250, 100)
    mouse_pos = pygame.mouse.get_pos()
    labels = (
        ("2 players", "AI vs AI")
        if custom_selected
        else ("Classic", "Custom")
    )
    for rect, label in zip((classic_rect, custom_rect), labels):
        hovered = rect.collidepoint(mouse_pos)
        visual_rect = rect.inflate(12, 12) if hovered else rect
        pygame.draw.rect(screen, (8, 10, 74), visual_rect.move(0, 6), border_radius=26)
        pygame.draw.rect(screen, (46, 49, 159), visual_rect, border_radius=26)
        pygame.draw.rect(screen, MENU_BORDER, visual_rect, 3, border_radius=26)
        draw_menu_label(screen, button_font, label, visual_rect)
    if custom_selected:
        back_rect = menu_selection_back_rect()
        back_visual = back_rect.inflate(8, 8) if back_rect.collidepoint(mouse_pos) else back_rect
        pygame.draw.rect(screen, (46, 49, 159), back_visual, border_radius=16)
        pygame.draw.rect(screen, MENU_BORDER, back_visual, 2, border_radius=16)
        draw_menu_label(screen, pygame.font.SysFont("segoeui", 20, bold=True), "Back", back_visual)
    return classic_rect, custom_rect


def menu_selection_back_rect() -> pygame.Rect:
    return pygame.Rect(28, 28, 112, 48)


def draw_menu_label(screen, font, label: str, rect: pygame.Rect) -> None:
    surface = font.render(label, True, (248, 249, 255))
    screen.blit(surface, surface.get_rect(center=rect.center))


def draw_custom_board(
    screen,
    title_font,
    button_font,
    columns: int,
    rows: int,
) -> tuple[pygame.Rect, ...]:
    screen.fill(MENU_BG)

    panel = pygame.Rect(MENU_WIDTH // 2 - 320, 116, 640, 480)
    pygame.draw.rect(screen, (8, 10, 74), panel.move(0, 10), border_radius=52)
    pygame.draw.rect(screen, (166, 166, 230), panel, border_radius=52)
    pygame.draw.rect(screen, (118, 136, 220), panel, 10, border_radius=52)

    title = title_font.render("Custom Board", True, (28, 31, 91))
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 78)))

    label_font = pygame.font.SysFont("segoeui", 38, bold=True)
    value_font = pygame.font.SysFont("segoeui", 42, bold=True)

    col_minus = pygame.Rect(panel.x + 82, panel.y + 150, 82, 82)
    col_plus = pygame.Rect(panel.x + 164, panel.y + 150, 82, 82)
    row_minus = pygame.Rect(panel.x + 394, panel.y + 150, 82, 82)
    row_plus = pygame.Rect(panel.x + 476, panel.y + 150, 82, 82)

    def draw_stepper(rect: pygame.Rect, text: str) -> pygame.Rect:
        visual = rect.inflate(8, 8) if rect.collidepoint(pygame.mouse.get_pos()) else rect
        pygame.draw.circle(screen, (91, 91, 222), visual.center, 38)
        pygame.draw.circle(screen, (118, 136, 220), visual.center, 38, 6)
        draw_menu_label(screen, value_font, text, visual)
        return rect

    draw_stepper(col_minus, "-")
    draw_stepper(col_plus, "+")
    draw_stepper(row_minus, "-")
    draw_stepper(row_plus, "+")

    size_label = pygame.Rect(panel.x + 246, panel.y + 150, 148, 82)
    size_visual = size_label
    pygame.draw.rect(screen, (248, 249, 255), size_visual, border_radius=24)
    pygame.draw.rect(screen, (118, 136, 220), size_visual, 4, border_radius=24)
    size_text = value_font.render(f"{columns} x {rows}", True, (28, 31, 91))
    screen.blit(size_text, size_text.get_rect(center=size_visual.center))

    start_rect = pygame.Rect(panel.centerx - 140, panel.y + 246, 280, 82)
    start_visual = start_rect.inflate(10, 10) if start_rect.collidepoint(pygame.mouse.get_pos()) else start_rect
    pygame.draw.rect(screen, (8, 10, 74), start_visual.move(0, 6), border_radius=24)
    pygame.draw.rect(screen, (46, 49, 159), start_visual, border_radius=24)
    pygame.draw.rect(screen, MENU_BORDER, start_visual, 3, border_radius=24)
    draw_menu_label(screen, button_font, "Start", start_visual)

    back_rect = pygame.Rect(28, 28, 92, 44)
    back_visual = back_rect.inflate(8, 8) if back_rect.collidepoint(pygame.mouse.get_pos()) else back_rect
    pygame.draw.rect(screen, (46, 49, 159), back_visual, border_radius=16)
    draw_menu_label(screen, pygame.font.SysFont("segoeui", 18, bold=True), "Back", back_visual)
    return col_minus, col_plus, row_minus, row_plus, start_rect, back_rect


def format_elapsed(elapsed: float) -> str:
    seconds = max(0, int(elapsed))
    minutes, remainder = divmod(seconds, 60)
    return f"{minutes:02d}:{remainder:02d}"


def draw_game_piece(screen, center, color, radius=38, asset=None) -> None:
    if asset is not None:
        piece = pygame.transform.smoothscale(asset, (radius * 2, radius * 2))
        screen.blit(piece, piece.get_rect(center=center))
        return
    cx, cy = center
    pygame.draw.circle(screen, color, (cx, cy), radius)
    pygame.draw.circle(screen, (255, 255, 255), (cx, cy), radius - 19)
    pygame.draw.circle(screen, color, (cx, cy), radius - 25)


def draw_player_card(
    screen,
    center_x,
    title: str,
    wins: int,
    is_human: bool,
    active: bool,
    piece_asset=None,
    fallback_color: tuple[int, int, int] | None = None,
) -> pygame.Rect:
    card = pygame.Rect(center_x - 82, 205, 164, 240)
    pygame.draw.rect(screen, (91, 91, 222), card, border_radius=28)
    pygame.draw.rect(screen, (118, 136, 220), card, 7, border_radius=28)

    piece_x = card.centerx
    card_piece_color = fallback_color or (COLOR_X if is_human else COLOR_O)
    draw_game_piece(screen, (piece_x, card.y + 86), card_piece_color, 44, piece_asset)

    name_font = pygame.font.SysFont("segoeui", 29, bold=True)
    small_font = pygame.font.SysFont("segoeui", 26, bold=True)
    name = name_font.render(title, True, (28, 31, 91))
    wins_text = small_font.render(f"{wins} win{'s' if wins != 1 else ''}", True, (28, 31, 91))
    screen.blit(name, name.get_rect(center=(piece_x, card.y + 154)))
    screen.blit(wins_text, wins_text.get_rect(center=(piece_x, card.y + 190)))

    if active:
        turn_font = pygame.font.SysFont("segoeui", 28, bold=True)
        turn_text = turn_font.render("Your turn" if is_human else "AI turn", True, (129, 136, 220))
        screen.blit(turn_text, turn_text.get_rect(center=(piece_x, card.bottom + 32)))
    return card


def draw_win_chance(
    screen,
    state: GameState,
    x_color: tuple[int, int, int] = COLOR_X,
    o_color: tuple[int, int, int] = COLOR_O,
) -> None:
    _, _, bar = game_layout(state)
    label_font = pygame.font.SysFont("segoeui", 20, bold=True)
    small_font = pygame.font.SysFont("segoeui", 17, bold=True)
    label = label_font.render("Win chance", True, (248, 249, 255))
    screen.blit(label, label.get_rect(center=(bar.centerx, bar.y - 22)))

    winner = state.winner()
    if winner == PLAYER_X:
        x_percent = 100
    elif winner == PLAYER_O:
        x_percent = 0
    else:
        x_percent = round(evaluation_fraction(evaluate(state.board, PLAYER_X)) * 100)
    o_percent = 100 - x_percent

    pygame.draw.rect(screen, (42, 44, 120), bar, border_radius=8)
    x_width = round(bar.width * x_percent / 100)
    if x_width:
        pygame.draw.rect(screen, x_color, (bar.x, bar.y, x_width, bar.height), border_radius=8)
    if x_width < bar.width:
        pygame.draw.rect(
            screen,
            o_color,
            (bar.x + x_width, bar.y, bar.width - x_width, bar.height),
            border_radius=8,
        )
    draw_text(screen, small_font, f"Player 1 {x_percent}%", (bar.x, bar.bottom + 8), x_color)
    computer_label = small_font.render(f"Computer {o_percent}%", True, o_color)
    screen.blit(computer_label, (bar.right - computer_label.get_width(), bar.bottom + 8))


def draw_benchmark_info(screen, item: dict | None) -> None:
    if item is None:
        return

    panel = pygame.Rect(24, 455, 300, 180)
    pygame.draw.rect(screen, (24, 28, 102), panel, border_radius=14)
    pygame.draw.rect(screen, (118, 136, 220), panel, 2, border_radius=14)
    body_font = pygame.font.SysFont("segoeui", 15)

    description = str(item["description"])
    words = description.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if body_font.size(candidate)[0] > panel.width - 24 and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    for index, line in enumerate(lines[:8]):
        if index == 7 and len(lines) > 8:
            while line and body_font.size(f"{line}...")[0] > panel.width - 24:
                line = line[:-1]
            line = f"{line.rstrip()}..."
        draw_text(screen, body_font, line, (panel.x + 12, panel.y + 12 + index * 19), (220, 224, 255))


def draw_benchmark_details(screen, item: dict) -> None:
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((8, 10, 45, 205))
    screen.blit(overlay, (0, 0))

    panel_width = min(900, screen.get_width() - 64)
    body_font = pygame.font.SysFont("segoeui", 19)
    description = str(item["description"])
    words = description.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if body_font.size(candidate)[0] > panel_width - 56 and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)

    panel_height = 48 + len(lines) * 30
    panel = pygame.Rect(0, 0, panel_width, panel_height)
    panel.center = screen.get_rect().center
    pygame.draw.rect(screen, (24, 28, 102), panel, border_radius=18)
    pygame.draw.rect(screen, (118, 136, 220), panel, 3, border_radius=18)
    for index, line in enumerate(lines):
        draw_text(
            screen,
            body_font,
            line,
            (panel.x + 26, panel.y + 24 + index * 30),
            (220, 224, 255),
        )


def game_layout(state: GameState) -> tuple[int, pygame.Rect, pygame.Rect]:
    """Return non-overlapping board and evaluation-bar geometry."""
    rows = len(state.board)
    columns = len(state.board[0]) if state.board else COLUMNS
    # Reserve room for the cards on each side and the evaluation bar below.
    cell = min(
        GAME_CELL,
        max(42, (GAME_HEIGHT - 148) // max(1, rows)),
        max(42, (GAME_WIDTH - 520) // max(1, columns)),
    )
    board_width = columns * cell
    board_height = rows * cell
    board_left = (GAME_WIDTH - board_width) // 2
    board_top = GAME_BOARD_TOP
    board_rect = pygame.Rect(board_left - 12, board_top - 12, board_width + 24, board_height + 24)
    bar = pygame.Rect(board_rect.left, board_rect.bottom + 42, board_rect.width, 24)
    return cell, board_rect, bar


def game_rematch_rect() -> pygame.Rect:
    return pygame.Rect(42, 28, 150, 66)


def ai_controls_layout(state: GameState) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
    _, board_rect, _ = game_layout(state)
    width = max(18, min(36, board_rect.left - 318))
    height = 34
    gap = 7
    left = board_rect.left - width - 8
    top = board_rect.centery - (height * 3 + gap * 2) // 2
    next_rect, pause_rect, previous_rect = tuple(
        pygame.Rect(left, top + index * (height + gap), width, height)
        for index in range(3)
    )
    return next_rect, pause_rect, previous_rect


def draw_ai_controls(screen, state: GameState, paused: bool, history_index: int) -> None:
    buttons = ai_controls_layout(state)
    labels = (">>", ">" if paused else "||", "<<")
    font = pygame.font.SysFont("segoeui", min(18, buttons[0].width - 4), bold=True)
    for index, (rect, label) in enumerate(zip(buttons, labels)):
        disabled = (index == 0 and state.is_terminal()) or (index == 2 and history_index == 0)
        fill = (37, 50, 76) if disabled else (46, 49, 159)
        if rect.collidepoint(pygame.mouse.get_pos()) and not disabled:
            fill = (75, 88, 185)
        pygame.draw.rect(screen, fill, rect, border_radius=8)
        pygame.draw.rect(screen, (118, 136, 220), rect, 2, border_radius=8)
        label_surface = font.render(label, True, (165, 170, 230) if disabled else (248, 249, 255))
        screen.blit(label_surface, label_surface.get_rect(center=rect.center))


def settings_layout(
    mode: str = "AI vs AI",
) -> tuple[pygame.Rect, pygame.Rect | None, list[pygame.Rect], pygame.Rect]:
    if mode == "Human vs Human":
        panel = pygame.Rect(815, 108, 420, 176)
        depth_track = None
        benchmark_buttons = []
        exit_rect = pygame.Rect(panel.x + 24, panel.y + 94, panel.width - 48, 42)
    elif mode == "Human vs AI":
        panel = pygame.Rect(815, 108, 420, 270)
        depth_track = pygame.Rect(panel.x + 36, panel.y + 116, panel.width - 72, 8)
        benchmark_buttons = []
        exit_rect = pygame.Rect(panel.x + 24, panel.y + 194, panel.width - 48, 42)
    else:
        panel = pygame.Rect(815, 108, 420, 410)
        depth_track = pygame.Rect(panel.x + 36, panel.y + 116, panel.width - 72, 8)
        benchmark_buttons = [
            pygame.Rect(panel.x + 24 + (index % 2) * 190, panel.y + 190 + (index // 2) * 48, 176, 38)
            for index in range(4)
        ]
        exit_rect = pygame.Rect(panel.x + 24, panel.y + 330, panel.width - 48, 42)
    return panel, depth_track, benchmark_buttons, exit_rect


def depth_from_slider(x: int, track: pygame.Rect) -> int:
    """Map a slider position to the supported search depth 1..7."""
    return set_search_depth(round((x - track.left) / track.width * 6 + 1))


def depth_slider_x(depth: int, track: pygame.Rect) -> int:
    return round(track.left + (clamp_depth(depth) - 1) * track.width / 6)


def draw_settings_panel(screen, depth: int, benchmark_index: int | None, mode: str) -> None:
    panel, depth_track, benchmark_buttons, exit_rect = settings_layout(mode)
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((8, 10, 45, 80))
    screen.blit(overlay, (0, 0))

    pygame.draw.rect(screen, (24, 28, 102), panel, border_radius=18)
    pygame.draw.rect(screen, (118, 136, 220), panel, 3, border_radius=18)
    title_font = pygame.font.SysFont("segoeui", 25, bold=True)
    label_font = pygame.font.SysFont("segoeui", 18, bold=True)
    title_text = "Game settings" if mode == "Human vs Human" else "Difficulty"
    title = title_font.render(title_text, True, (248, 249, 255))
    screen.blit(title, (panel.x + 24, panel.y + 18))
    if depth_track is not None:
        draw_text(
            screen,
            label_font,
            f"Max depth: {depth}",
            (panel.x + 190, panel.y + 22),
            (200, 204, 255),
        )

        pygame.draw.rect(screen, (46, 49, 159), depth_track, border_radius=4)
        knob_x = depth_slider_x(depth, depth_track)
        pygame.draw.line(
            screen,
            (129, 140, 248),
            (depth_track.left, depth_track.centery),
            (knob_x, depth_track.centery),
            8,
        )
        for index in range(1, 8):
            x = depth_slider_x(index, depth_track)
            pygame.draw.circle(screen, (248, 249, 255), (x, depth_track.centery), 4)
        pygame.draw.circle(screen, (248, 249, 255), (knob_x, depth_track.centery), 11)
        pygame.draw.circle(screen, (99, 102, 241), (knob_x, depth_track.centery), 7)
        draw_text(screen, label_font, "1", (depth_track.left - 4, depth_track.y + 12))
        end_label = label_font.render("7", True, (248, 249, 255))
        screen.blit(end_label, (depth_track.right - end_label.get_width() + 4, depth_track.y + 12))

    if benchmark_buttons:
        replay_title = label_font.render("Replay sample boards", True, (248, 249, 255))
        screen.blit(replay_title, (panel.x + 24, panel.y + 158))
    for index, rect in enumerate(benchmark_buttons):
        active = index == benchmark_index
        fill = (99, 102, 241) if active else (46, 49, 159)
        pygame.draw.rect(screen, fill, rect, border_radius=9)
        pygame.draw.rect(screen, (165, 180, 252), rect, 2, border_radius=9)
        label = label_font.render(f"Replay B{index + 1}", True, (248, 249, 255))
        screen.blit(label, label.get_rect(center=rect.center))

    pygame.draw.rect(screen, (63, 67, 175), exit_rect, border_radius=10)
    pygame.draw.rect(screen, (165, 180, 252), exit_rect, 2, border_radius=10)
    exit_label = label_font.render("Exit to main menu", True, (248, 249, 255))
    screen.blit(exit_label, exit_label.get_rect(center=exit_rect.center))


def draw_game_screen(
    screen,
    state: GameState,
    elapsed: float,
    human_wins: int,
    computer_wins: int,
    depth: int,
    settings_open: bool,
    benchmark_index: int | None,
    piece_assets: dict[str, object],
    mode: str,
    benchmark_item: dict | None = None,
    benchmark_details_open: bool = False,
    history_index: int = 0,
    paused: bool = False,
) -> None:
    screen.fill(MENU_BG)
    board_rows = len(state.board)
    board_columns = len(state.board[0]) if state.board else COLUMNS
    cell, board_rect, _ = game_layout(state)
    board_left = board_rect.left + 12
    board_top = board_rect.top + 12
    x_color = piece_accent_color(piece_assets.get(PLAYER_X), COLOR_X)
    o_color = piece_accent_color(piece_assets.get(PLAYER_O), COLOR_O)

    rematch_rect = game_rematch_rect()
    rematch_visual = rematch_rect.inflate(8, 8) if rematch_rect.collidepoint(pygame.mouse.get_pos()) else rematch_rect
    pygame.draw.rect(screen, (46, 49, 159), rematch_visual, border_radius=18)
    pygame.draw.rect(screen, MENU_BORDER, rematch_visual, 3, border_radius=18)
    draw_menu_label(screen, pygame.font.SysFont("segoeui", 24, bold=True), "Rematch", rematch_visual)

    draw_gear(screen, (GAME_WIDTH - 54, 54), 11)

    pygame.draw.rect(screen, (91, 91, 222), board_rect, border_radius=18)

    for row in range(board_rows):
        for col in range(board_columns):
            cx = board_left + col * cell + cell // 2
            cy = board_top + row * cell + cell // 2
            token = state.board[row][col]
            color = x_color if token == PLAYER_X else o_color if token == PLAYER_O else (42, 44, 120)
            piece_radius = max(18, cell // 2 - 6)
            if token in piece_assets:
                piece_size = piece_radius * 2
                piece = pygame.transform.smoothscale(piece_assets[token], (piece_size, piece_size))
                screen.blit(piece, piece.get_rect(center=(cx, cy)))
            else:
                pygame.draw.circle(screen, color, (cx, cy), piece_radius)
                pygame.draw.circle(screen, (118, 136, 220), (cx, cy), piece_radius, 2)

    human_active = not state.is_terminal() and state.to_move == HUMAN
    ai_active = not state.is_terminal() and state.to_move == AI
    right_title = "Player 2" if mode == "Human vs Human" else "Computer"
    draw_player_card(
        screen,
        220,
        "Player 1",
        human_wins,
        True,
        human_active,
        piece_assets.get(PLAYER_X),
        x_color,
    )
    draw_player_card(
        screen,
        GAME_WIDTH - 220,
        right_title,
        computer_wins,
        mode == "Human vs Human",
        ai_active,
        piece_assets.get(PLAYER_O),
        o_color,
    )
    draw_win_chance(screen, state, x_color, o_color)
    draw_benchmark_info(screen, benchmark_item)
    if mode == "AI vs AI":
        draw_ai_controls(screen, state, paused, history_index)
    if benchmark_item is not None and benchmark_details_open:
        draw_benchmark_details(screen, benchmark_item)

    if state.is_terminal():
        winner = state.winner()
        if winner == HUMAN:
            status = "Player 1 wins"
        elif winner == AI:
            status = "Player 2 wins" if mode == "Human vs Human" else "Computer wins"
        else:
            status = "Draw"
        status_font = pygame.font.SysFont("segoeui", 32, bold=True)
        status_surface = status_font.render(status, True, (248, 249, 255))
        screen.blit(status_surface, status_surface.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT - 34)))

    # Legacy game tools remain available through R, F11, and keyboard AI controls.
    # draw_evaluation(screen, fonts, state.board)
    if settings_open:
        draw_settings_panel(screen, depth, benchmark_index, mode)


def draw_setup_piece(screen, center, ring_color=MENU_YELLOW, asset=None) -> None:
    cx, cy = center
    pygame.draw.rect(screen, (12, 15, 76), (cx - 65, cy - 65, 130, 130), border_radius=24)
    pygame.draw.rect(screen, (118, 136, 220), (cx - 65, cy - 65, 130, 130), 12, border_radius=24)
    if asset is not None:
        piece = pygame.transform.smoothscale(asset, (84, 84))
        screen.blit(piece, piece.get_rect(center=(cx, cy)))
        return
    pygame.draw.circle(screen, ring_color, (cx, cy), 42)
    pygame.draw.circle(screen, (248, 249, 255), (cx, cy), 24)


def draw_setup_icon(screen, center, kind: str) -> pygame.Rect:
    cx, cy = center
    rect = pygame.Rect(cx - 38, cy - 38, 76, 76)
    scale = 1.12 if rect.collidepoint(pygame.mouse.get_pos()) else 1.0
    pygame.draw.circle(screen, (112, 105, 234), (cx, cy), int(38 * scale))
    pygame.draw.circle(screen, (66, 51, 185), (cx, cy), int(29 * scale))
    dx = int(18 * scale)
    dy = int(17 * scale)
    if kind == "first":
        pygame.draw.polygon(
            screen,
            (248, 249, 255),
            [(cx - dx, cy + dy), (cx - 8, cy - dy), (cx - 4, cy + 10), (cx + 13, cy - dy), (cx + dx, cy - dy), (cx + 2, cy + dy)],
        )
        pygame.draw.line(screen, (248, 249, 255), (cx - 20, cy + 20), (cx + 20, cy - 20), 3)
    else:
        pygame.draw.line(screen, (248, 249, 255), (cx - dx, cy), (cx + dx, cy), 5)
        pygame.draw.polygon(screen, (248, 249, 255), [(cx - dx - 2, cy), (cx - 9, cy - 10), (cx - 9, cy + 10)])
        pygame.draw.polygon(screen, (248, 249, 255), [(cx + dx + 2, cy), (cx + 9, cy - 10), (cx + 9, cy + 10)])
    return rect


def classic_setup_controls() -> tuple[pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect]:
    start_rect = pygame.Rect(MENU_WIDTH // 2 - 140, 510, 280, 100)
    swap_rect = pygame.Rect(MENU_WIDTH // 2 - 38, 334, 76, 76)
    random_rect = pygame.Rect(MENU_WIDTH // 2 - 180, 432, 170, 44)
    default_rect = pygame.Rect(MENU_WIDTH // 2 + 10, 432, 170, 44)
    return start_rect, swap_rect, random_rect, default_rect


def draw_classic_setup(
    screen,
    title_font,
    label_font,
    button_font,
    player_asset=None,
    computer_asset=None,
    mode: str = "Human vs AI",
) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect]:
    screen.fill(MENU_BG)

    left_x = MENU_WIDTH // 2 - 300
    right_x = MENU_WIDTH // 2 + 300
    card_y = 222

    left_rect = pygame.Rect(left_x - 90, card_y - 46, 180, 230)
    right_rect = pygame.Rect(right_x - 90, card_y - 46, 180, 230)
    for rect in (left_rect, right_rect):
        pygame.draw.rect(screen, (91, 91, 222), rect, border_radius=24)
        pygame.draw.rect(screen, (118, 136, 220), rect, 3, border_radius=24)

    draw_setup_piece(screen, (left_x, card_y + 30), COLOR_X, player_asset)
    draw_setup_piece(screen, (right_x, card_y + 30), COLOR_O, computer_asset)

    label_rect_y = card_y + 124
    draw_menu_label(screen, label_font, "Player 1", pygame.Rect(left_x - 80, label_rect_y, 160, 50))
    right_name = "2 players" if mode == "Human vs Human" else "Computer"
    draw_menu_label(screen, label_font, right_name, pygame.Rect(right_x - 80, label_rect_y, 160, 50))

    vs = title_font.render("VS", True, (248, 249, 255))
    screen.blit(vs, vs.get_rect(center=(MENU_WIDTH // 2, card_y + 12)))

    _, swap_rect, random_rect, default_rect = classic_setup_controls()
    draw_setup_icon(screen, swap_rect.center, "swap")
    setup_button_font = pygame.font.SysFont("segoeui", 20, bold=True)
    for rect, label in ((random_rect, "Random"), (default_rect, "Default")):
        visual = rect.inflate(6, 4) if rect.collidepoint(pygame.mouse.get_pos()) else rect
        pygame.draw.rect(screen, (46, 49, 159), visual, border_radius=14)
        pygame.draw.rect(screen, MENU_BORDER, visual, 2, border_radius=14)
        draw_menu_label(screen, setup_button_font, label, visual)

    start_rect, _, _, _ = classic_setup_controls()
    start_visual = start_rect.inflate(12, 12) if start_rect.collidepoint(pygame.mouse.get_pos()) else start_rect
    pygame.draw.rect(screen, (8, 10, 74), start_visual.move(0, 6), border_radius=26)
    pygame.draw.rect(screen, (46, 49, 159), start_visual, border_radius=26)
    pygame.draw.rect(screen, MENU_BORDER, start_visual, 3, border_radius=26)
    draw_menu_label(screen, button_font, "Start", start_visual)

    back_rect = pygame.Rect(28, 28, 92, 44)
    back_visual = back_rect.inflate(8, 8) if back_rect.collidepoint(pygame.mouse.get_pos()) else back_rect
    pygame.draw.rect(screen, (46, 49, 159), back_visual, border_radius=16)
    draw_menu_label(screen, pygame.font.SysFont("segoeui", 18, bold=True), "Back", back_visual)
    return start_rect, swap_rect, random_rect, default_rect


def status_text(state: GameState, mode: str, depth: int, error: str) -> str:
    if error:
        return error
    if state.is_terminal():
        winner = state.winner()
        return f"{winner} wins — press R to restart" if winner else "Draw — press R to restart"
    if mode == "Human vs Human":
        actor = "Player 1" if state.to_move == HUMAN else "Player 2"
    else:
        actor = "Human" if mode == "Human vs AI" and state.to_move == HUMAN else "AI"
    return f"{actor} ({state.to_move}) to move | depth {depth}"


def choose_ai_move(state: GameState, depth: int) -> int:
    moves = legal_moves(state.board)
    if state.is_terminal() or not moves:
        raise ValueError("No legal move is available.")
    reset_node_counters()
    requested_depth = clamp_depth(depth)
    column, _ = alphabeta(
        state.board,
        state.to_move,
        requested_depth,
        state.to_move,
    )
    if column not in moves:
        raise ValueError(f"AI returned illegal column {column}.")
    return column


def apply_human_move(state: GameState, column: int) -> GameState:
    """Apply one human move after enforcing turn, terminal, and legal-move rules."""
    if state.is_terminal():
        raise ValueError("The game is already over.")
    if column not in legal_moves(state.board):
        raise ValueError(f"Column {column + 1} is full or unavailable.")
    return state.apply(column)


def apply_ai_move(state: GameState, depth: int) -> GameState:
    """Apply one guarded AI move for Human vs AI or AI vs AI mode."""
    if state.is_terminal():
        raise ValueError("The game is already over.")
    return state.apply(choose_ai_move(state, depth))


def main() -> None:
    pygame.init()
    pygame.display.set_caption("AI Board Game Arena — Connect Four")
    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_icon(load_window_icon())
    piece_library = load_piece_library()
    available_pieces = list(piece_library.values())
    default_player_piece, default_computer_piece = default_piece_pair(piece_library)
    player_piece = default_player_piece
    computer_piece = default_computer_piece
    clock = pygame.time.Clock()
    menu_title_font = pygame.font.SysFont("segoeui", 72, bold=True)
    menu_button_font = pygame.font.SysFont("segoeui", 38, bold=True)
    title_font = pygame.font.SysFont("segoeui", 30, bold=True)
    label_font = pygame.font.SysFont("segoeui", 23, bold=True)
    small_font = pygame.font.SysFont("segoeui", 18)
    fonts = (label_font, small_font)
    phase = "menu"
    custom_selected = False
    custom_columns = 7
    custom_rows = 6

    benchmarks = load_benchmarks()
    benchmark_index = None
    mode = "Human vs AI"
    human_starts = True
    depth = 4
    paused = False
    settings_open = False
    depth_dragging = False
    benchmark_details_open = False
    ai_due_at = 0.0
    error = ""
    state = GameState.new(first_player=PLAYER_X)
    history_states = [state]
    history_index = 0
    benchmark_description = ""
    human_wins = 0
    computer_wins = 0
    game_started_at = time.monotonic()
    recorded_result = None

    def restart() -> None:
        nonlocal state, history_states, history_index, paused, settings_open, benchmark_index, benchmark_details_open, error, benchmark_description, ai_due_at, game_started_at, recorded_result
        state = GameState.new(first_player=HUMAN if human_starts else AI)
        history_states = [state]
        history_index = 0
        paused = False
        settings_open = False
        benchmark_index = None
        benchmark_details_open = False
        error = ""
        benchmark_description = ""
        ai_due_at = 0.0
        game_started_at = time.monotonic()
        recorded_result = None

    def load_benchmark(index: int) -> None:
        nonlocal state, history_states, history_index, benchmark_index, paused, benchmark_details_open, error, benchmark_description, ai_due_at, recorded_result, game_started_at
        benchmark_index = index % len(benchmarks)
        item = benchmarks[benchmark_index]
        state = benchmark_state(item)
        history_states = [state]
        history_index = 0
        paused = True
        benchmark_details_open = True
        error = ""
        benchmark_description = item["description"]
        ai_due_at = 0.0
        recorded_result = None
        game_started_at = time.monotonic()

    def rematch_game() -> None:
        if benchmark_index is None:
            restart()
        else:
            load_benchmark(benchmark_index)

    def clear_recorded_result() -> None:
        nonlocal human_wins, computer_wins, recorded_result
        if recorded_result == HUMAN:
            human_wins = max(0, human_wins - 1)
        elif recorded_result == AI:
            computer_wins = max(0, computer_wins - 1)
        recorded_result = None

    def record_state(next_state: GameState) -> None:
        nonlocal state, history_states, history_index
        state = next_state
        history_states = history_states[:history_index + 1]
        history_states.append(state)
        history_index += 1

    def step_forward() -> None:
        nonlocal state, history_index, paused, benchmark_details_open, ai_due_at, error
        paused = True
        benchmark_details_open = False
        ai_due_at = 0.0
        if history_index < len(history_states) - 1:
            if state.is_terminal():
                clear_recorded_result()
            history_index += 1
            state = history_states[history_index]
            return
        if state.is_terminal():
            return
        try:
            record_state(apply_ai_move(state, depth))
            error = ""
        except ValueError as exc:
            error = str(exc)

    def step_backward() -> None:
        nonlocal state, history_index, paused, benchmark_details_open, ai_due_at
        if history_index == 0:
            return
        if state.is_terminal():
            clear_recorded_result()
        history_index -= 1
        state = history_states[history_index]
        paused = True
        benchmark_details_open = False
        ai_due_at = 0.0

    running = True
    while running:
        now = time.monotonic()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif phase == "menu":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    classic_rect = pygame.Rect(MENU_WIDTH // 2 - 265, 500, 250, 100)
                    custom_rect = pygame.Rect(MENU_WIDTH // 2 + 15, 500, 250, 100)
                    if custom_selected:
                        if menu_selection_back_rect().collidepoint(event.pos):
                            custom_selected = False
                        elif classic_rect.collidepoint(event.pos):
                            mode = "Human vs Human"
                            phase = "custom_board"
                        elif custom_rect.collidepoint(event.pos):
                            mode = "AI vs AI"
                            phase = "custom_board"
                    elif classic_rect.collidepoint(event.pos):
                        mode = "Human vs AI"
                        custom_selected = False
                        game_engine_module.set_board_config(6, 7, 4)
                        student_core_module.set_ai_board_config(6, 7, 4)
                        phase = "classic_setup"
                    elif custom_rect.collidepoint(event.pos):
                        custom_selected = True
            elif phase == "custom_board":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    panel = pygame.Rect(MENU_WIDTH // 2 - 320, 116, 640, 480)
                    col_minus = pygame.Rect(panel.x + 82, panel.y + 150, 82, 82)
                    col_plus = pygame.Rect(panel.x + 164, panel.y + 150, 82, 82)
                    row_minus = pygame.Rect(panel.x + 394, panel.y + 150, 82, 82)
                    row_plus = pygame.Rect(panel.x + 476, panel.y + 150, 82, 82)
                    start_rect = pygame.Rect(panel.centerx - 140, panel.y + 246, 280, 82)
                    back_rect = pygame.Rect(28, 28, 92, 44)
                    if back_rect.collidepoint(event.pos):
                        phase = "menu"
                    elif col_minus.collidepoint(event.pos):
                        custom_columns = max(7, custom_columns - 1)
                    elif col_plus.collidepoint(event.pos):
                        custom_columns = min(9, custom_columns + 1)
                    elif row_minus.collidepoint(event.pos):
                        custom_rows = max(6, custom_rows - 1)
                    elif row_plus.collidepoint(event.pos):
                        custom_rows = min(8, custom_rows + 1)
                    elif start_rect.collidepoint(event.pos):
                        game_engine_module.set_board_config(custom_rows, custom_columns, 4)
                        student_core_module.set_ai_board_config(custom_rows, custom_columns, 4)
                        phase = "classic_setup"
            elif phase == "classic_setup":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    start_rect, swap_rect, random_rect, default_rect = classic_setup_controls()
                    back_rect = pygame.Rect(28, 28, 92, 44)
                    if back_rect.collidepoint(event.pos):
                        custom_selected = False
                        phase = "menu"
                    elif swap_rect.collidepoint(event.pos):
                        player_piece, computer_piece = computer_piece, player_piece
                    elif random_rect.collidepoint(event.pos):
                        player_piece, computer_piece = random_piece_pair(available_pieces)
                    elif default_rect.collidepoint(event.pos):
                        player_piece, computer_piece = default_player_piece, default_computer_piece
                    elif start_rect.collidepoint(event.pos):
                        phase = "game"
                        restart()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    rematch_game()
                elif event.key == pygame.K_z and event.mod & pygame.KMOD_CTRL:
                    restart()
                elif event.key == pygame.K_ESCAPE:
                    settings_open = False
                    benchmark_details_open = False
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_SPACE and mode == "AI vs AI":
                    benchmark_details_open = False
                    paused = not paused
                elif event.key in (pygame.K_n, pygame.K_RIGHT) and (mode == "AI vs AI" or benchmark_description):
                    step_forward()
                elif event.key in (pygame.K_m, pygame.K_LEFT) and (mode == "AI vs AI" or benchmark_description):
                    step_backward()
                elif event.key == pygame.K_i and benchmark_description:
                    paused = True
                    benchmark_details_open = not benchmark_details_open
            elif event.type == pygame.MOUSEMOTION and depth_dragging and settings_open:
                _, depth_track, _, _ = settings_layout(mode)
                if depth_track is not None:
                    depth = depth_from_slider(event.pos[0], depth_track)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                rematch_rect = game_rematch_rect()
                if rematch_rect.collidepoint(event.pos):
                    rematch_game()
                    continue
                gear_rect = pygame.Rect(GAME_WIDTH - 92, 16, 76, 76)
                if gear_rect.collidepoint(event.pos):
                    settings_open = not settings_open
                    continue
                if benchmark_details_open:
                    benchmark_details_open = False
                    continue
                if settings_open:
                    _, depth_track, benchmark_buttons, exit_rect = settings_layout(mode)
                    if exit_rect.collidepoint(event.pos):
                        phase = "menu"
                        settings_open = False
                        continue
                    for selected_benchmark, rect in enumerate(benchmark_buttons):
                        if rect.collidepoint(event.pos):
                            mode = "AI vs AI"
                            load_benchmark(selected_benchmark)
                            settings_open = False
                            phase = "game"
                            break
                    else:
                        if depth_track is not None and depth_track.inflate(24, 28).collidepoint(event.pos):
                            depth = depth_from_slider(event.pos[0], depth_track)
                            depth_dragging = True
                    continue
                if mode == "AI vs AI":
                    next_rect, pause_rect, previous_rect = ai_controls_layout(state)
                    if next_rect.collidepoint(event.pos):
                        step_forward()
                        continue
                    if pause_rect.collidepoint(event.pos):
                        paused = not paused
                        benchmark_details_open = False
                        continue
                    if previous_rect.collidepoint(event.pos):
                        step_backward()
                        continue
                if mode in ("Human vs AI", "Human vs Human") and not state.is_terminal():
                    if mode == "Human vs AI" and state.to_move != HUMAN:
                        continue
                    board_rows = len(state.board)
                    board_columns = len(state.board[0]) if state.board else COLUMNS
                    cell, board_rect, _ = game_layout(state)
                    board_left = board_rect.left + 12
                    board_top = board_rect.top + 12
                    if board_left <= x < board_left + board_columns * cell and board_top <= y < board_top + board_rows * cell:
                        column = (x - board_left) // cell
                        try:
                            state = apply_human_move(state, column)
                            error = ""
                        except ValueError as exc:
                            error = str(exc)
            elif event.type == pygame.MOUSEBUTTONUP:
                depth_dragging = False

        if phase == "menu":
            draw_menu(
                screen,
                menu_title_font,
                menu_button_font,
                small_font,
                custom_selected,
            )
            pygame.display.flip()
            clock.tick(30)
            continue
        if phase == "custom_board":
            draw_custom_board(
                screen,
                menu_title_font,
                menu_button_font,
                custom_columns,
                custom_rows,
            )
            pygame.display.flip()
            clock.tick(30)
            continue
        if phase == "classic_setup":
            draw_classic_setup(
                screen,
                menu_title_font,
                label_font,
                menu_button_font,
                player_piece,
                computer_piece,
                mode,
            )
            pygame.display.flip()
            clock.tick(30)
            continue

        ai_turn = mode == "AI vs AI" or (mode == "Human vs AI" and state.to_move == AI)
        if ai_turn and not paused and not state.is_terminal() and now >= ai_due_at:
            try:
                record_state(apply_ai_move(state, depth))
                error = ""
                ai_due_at = now + (0.45 if mode == "AI vs AI" else 0.0)
            except ValueError as exc:
                error = str(exc)
                paused = True

        if state.is_terminal() and recorded_result is None:
            winner = state.winner()
            if winner == HUMAN:
                human_wins += 1
            elif winner == AI:
                computer_wins += 1
            recorded_result = winner or "draw"

        depth_label = f"Search depth: {depth}"
        draw_game_screen(
            screen,
            state,
            now - game_started_at,
            human_wins,
            computer_wins,
            depth,
            settings_open,
            benchmark_index,
            {PLAYER_X: player_piece, PLAYER_O: computer_piece},
            mode,
            benchmarks[benchmark_index] if benchmark_index is not None else None,
            benchmark_details_open,
            history_index,
            paused=paused,
        )
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
