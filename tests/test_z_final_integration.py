"""F02 acceptance tests for the final Alpha-Beta application integration."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
STARTER_DIR = PROJECT_DIR / "starter"
sys.path.insert(0, str(STARTER_DIR))

import game_engine as ge  # noqa: E402


def _app():
    import app

    return app


def _benchmark_state(state_id: str) -> ge.GameState:
    app = _app()
    item = next(item for item in app.load_benchmarks() if item["id"] == state_id)
    return ge.GameState(ge.board_from_rows(item["board"]), item["to_move"])


def test_alpha_beta_adapter_returns_legal_move():
    app = _app()
    state = ge.GameState.new()
    move = app.choose_ai_move(state, depth=1)
    assert move in ge.legal_moves(state.board)


def test_alpha_beta_adapter_blocks_b2_immediate_threat():
    app = _app()
    state = _benchmark_state("B2_depth_sensitive_block")
    assert app.choose_ai_move(state, depth=2) == 3


def test_alpha_beta_adapter_never_uses_full_b4_column():
    app = _app()
    state = _benchmark_state("B4_full_column_failure")
    assert 3 not in ge.legal_moves(state.board)
    assert app.choose_ai_move(state, depth=1) != 3


def test_alpha_beta_adapter_rejects_terminal_state():
    app = _app()
    board = ge.board_from_rows(
        [
            ".......",
            ".......",
            ".......",
            ".......",
            ".......",
            "XXXX...",
        ]
    )
    with pytest.raises(ValueError, match="No legal move"):
        app.choose_ai_move(ge.GameState(board, ge.PLAYER_O), depth=1)


def test_final_app_uses_alpha_beta_not_random_agent():
    app = _app()
    source = (STARTER_DIR / "app.py").read_text(encoding="utf-8")
    assert "from student_core import alphabeta, evaluate" in source
    assert "RandomAgent" not in source


def test_human_move_applies_only_on_human_turn():
    app = _app()
    state = ge.GameState.new(first_player=ge.PLAYER_X)
    updated = app.apply_human_move(state, 2)
    assert updated.board[ge.ROWS - 1][2] == ge.PLAYER_X
    assert updated.to_move == ge.PLAYER_O


def test_human_move_rejects_full_column_without_mutating_state():
    app = _app()
    board = ge.new_board()
    for row in range(ge.ROWS):
        board = ge.apply_move(
            board,
            0,
            ge.PLAYER_X if row % 2 == 0 else ge.PLAYER_O,
        )
    state = ge.GameState(board, ge.PLAYER_X)
    with pytest.raises(ValueError, match="full"):
        app.apply_human_move(state, 0)
    assert state.board == board


def test_human_move_rejects_terminal_state():
    app = _app()
    board = ge.board_from_rows(
        [
            ".......",
            ".......",
            ".......",
            ".......",
            ".......",
            "XXXX...",
        ]
    )
    with pytest.raises(ValueError, match="already over"):
        app.apply_human_move(ge.GameState(board, ge.PLAYER_X), 4)


def test_restart_state_is_clean_and_starts_with_x():
    state = ge.GameState.new(first_player=ge.PLAYER_X)
    state = state.apply(0)
    restarted = ge.GameState.new(first_player=ge.PLAYER_X)
    assert all(cell == ge.EMPTY for row in restarted.board for cell in row)
    assert restarted.to_move == ge.PLAYER_X
    assert restarted.board != state.board


def test_ai_vs_ai_moves_are_legal_and_alternate_turns():
    app = _app()
    state = ge.GameState.new(first_player=ge.PLAYER_X)
    for _ in range(6):
        previous_board = state.board
        previous_player = state.to_move
        state = app.apply_ai_move(state, depth=1)
        assert state.board != previous_board
        assert state.to_move == ge.other_player(previous_player)
        assert all(
            cell in (ge.EMPTY, ge.PLAYER_X, ge.PLAYER_O)
            for row in state.board
            for cell in row
        )
        if state.is_terminal():
            break


def test_ai_move_rejects_terminal_state():
    app = _app()
    board = ge.board_from_rows(
        [
            ".......",
            ".......",
            ".......",
            ".......",
            ".......",
            "XXXX...",
        ]
    )
    with pytest.raises(ValueError, match="already over"):
        app.apply_ai_move(ge.GameState(board, ge.PLAYER_O), depth=1)


def test_ai_vs_ai_controls_and_observable_delay_are_declared():
    source = (STARTER_DIR / "app.py").read_text(encoding="utf-8")
    assert 'mode = "AI vs AI"' in source
    assert "pygame.K_SPACE" in source
    assert "pygame.K_n" in source
    assert "ai_due_at = now + (0.45 if mode == \"AI vs AI\" else 0.0)" in source


@pytest.mark.parametrize("requested", range(1, 8))
def test_search_depth_accepts_all_product_values(requested):
    app = _app()
    assert app.set_search_depth(requested) == requested


@pytest.mark.parametrize(
    ("requested", "expected"),
    [(-100, 1), (0, 1), (8, 7), (100, 7)],
)
def test_search_depth_clamps_out_of_range_values(requested, expected):
    app = _app()
    assert app.set_search_depth(requested) == expected


def test_depth_1_and_depth_7_both_produce_legal_ai_moves():
    app = _app()
    for depth in (1, 7):
        state = ge.GameState.new(first_player=ge.PLAYER_X)
        move = app.choose_ai_move(state, depth)
        assert move in ge.legal_moves(state.board)


def test_ai_search_uses_the_requested_depth_without_time_capping(monkeypatch):
    app = _app()
    state = ge.GameState.new(first_player=ge.PLAYER_X)
    searched_depths = []

    def fake_alphabeta(board, player, depth, maximizing_player):
        searched_depths.append(depth)
        return ge.legal_moves(board)[0], 0.0

    monkeypatch.setattr(app, "alphabeta", fake_alphabeta)
    move = app.choose_ai_move(state, 7)

    assert move in ge.legal_moves(state.board)
    assert searched_depths == [7]


def test_depth_control_is_visible_and_updates_from_slider():
    source = (STARTER_DIR / "app.py").read_text(encoding="utf-8")
    assert 'f"Max depth: {depth}"' in source
    assert "set_search_depth(round" in source
    assert "depth = 4" in source


def test_search_depth_slider_maps_track_endpoints_and_steps():
    app = _app()
    _, track, _, _ = app.settings_layout()
    assert app.depth_from_slider(track.left, track) == 1
    assert app.depth_from_slider(track.right, track) == 7
    for depth in range(1, 8):
        assert app.depth_from_slider(app.depth_slider_x(depth, track), track) == depth


def test_settings_controls_are_specific_to_each_mode():
    app = _app()
    _, classic_depth, classic_benchmarks, _ = app.settings_layout("Human vs AI")
    _, players_depth, players_benchmarks, _ = app.settings_layout("Human vs Human")
    _, exhibition_depth, exhibition_benchmarks, _ = app.settings_layout("AI vs AI")

    assert classic_depth is not None
    assert classic_benchmarks == []
    assert players_depth is None
    assert players_benchmarks == []
    assert exhibition_depth is not None
    assert len(exhibition_benchmarks) == 4


def test_ai_vs_ai_history_controls_fit_left_of_standard_and_custom_boards():
    app = _app()
    states = (
        SimpleNamespace(board=[["."] * 7 for _ in range(6)]),
        SimpleNamespace(board=[["."] * 9 for _ in range(8)]),
    )
    for state in states:
        _, board_rect, _ = app.game_layout(state)
        next_button, pause, previous = app.ai_controls_layout(state)
        assert next_button.right <= board_rect.left
        assert pause.right <= board_rect.left
        assert previous.right <= board_rect.left
        assert previous.left >= 302
        assert next_button.bottom < pause.top
        assert pause.bottom < previous.top


def test_ai_vs_ai_game_screen_renders_pause_controls(monkeypatch):
    app = _app()
    app.pygame.init()
    monkeypatch.setattr(app.pygame.mouse, "get_pos", lambda: (0, 0))
    screen = app.pygame.Surface((app.GAME_WIDTH, app.GAME_HEIGHT))
    app.draw_game_screen(
        screen,
        ge.GameState.new(),
        0,
        0,
        0,
        4,
        False,
        None,
        {},
        "AI vs AI",
        paused=True,
    )


def test_game_screen_shows_rematch_in_each_play_mode(monkeypatch):
    app = _app()
    app.pygame.init()
    assert app.game_rematch_rect() == app.pygame.Rect(42, 28, 150, 66)
    monkeypatch.setattr(app.pygame.mouse, "get_pos", lambda: (0, 0))
    labels = []
    monkeypatch.setattr(
        app,
        "draw_menu_label",
        lambda _screen, _font, label, _rect: labels.append(label),
    )
    screen = app.pygame.Surface((app.GAME_WIDTH, app.GAME_HEIGHT))
    state = ge.GameState.new()
    for mode in ("Human vs AI", "Human vs Human", "AI vs AI"):
        labels.clear()
        app.draw_game_screen(screen, state, 0, 0, 0, 4, False, None, {}, mode)
        assert "Rematch" in labels


def test_default_and_random_piece_pairs_use_available_assets():
    app = _app()
    blue, amber, extra = object(), object(), object()
    assert app.default_piece_pair(
        {
            "huy-hieu-xanh-lam.png": blue,
            "huy-hieu-ho-phach.png": amber,
            "other.png": extra,
        }
    ) == (blue, amber)
    random_player, random_computer = app.random_piece_pair([blue, amber, extra])
    assert random_player in (blue, amber, extra)
    assert random_computer in (blue, amber, extra)
    assert random_player is not random_computer


def test_piece_accent_color_uses_icon_dominant_hue():
    app = _app()
    app.pygame.init()
    blue = app.pygame.Surface((12, 12), app.pygame.SRCALPHA)
    amber = app.pygame.Surface((12, 12), app.pygame.SRCALPHA)
    blue.fill((45, 120, 240, 255))
    amber.fill((250, 185, 20, 255))
    blue_accent = app.piece_accent_color(blue, app.COLOR_O)
    amber_accent = app.piece_accent_color(amber, app.COLOR_X)
    assert blue_accent[2] > blue_accent[0]
    assert amber_accent[0] > amber_accent[2]


def test_settings_gear_is_drawn_for_two_player_mode_too(monkeypatch):
    app = _app()
    app.pygame.init()
    monkeypatch.setattr(app.pygame.mouse, "get_pos", lambda: (0, 0))
    drawn_gears = []
    monkeypatch.setattr(
        app,
        "draw_gear",
        lambda *_args: drawn_gears.append(True) or app.pygame.Rect(0, 0, 1, 1),
    )
    screen = app.pygame.Surface((app.GAME_WIDTH, app.GAME_HEIGHT))
    state = ge.GameState.new()
    common_args = (screen, state, 0, 0, 0, 4, False, None, {})

    app.draw_game_screen(*common_args, "Human vs Human")
    assert len(drawn_gears) == 1
    app.draw_game_screen(*common_args, "Human vs AI")
    assert len(drawn_gears) == 2


def test_custom_mode_chooser_displays_back_button(monkeypatch):
    app = _app()
    app.pygame.init()
    monkeypatch.setattr(app.pygame.mouse, "get_pos", lambda: (0, 0))
    labels = []
    monkeypatch.setattr(
        app,
        "draw_menu_label",
        lambda _screen, _font, label, _rect: labels.append(label),
    )
    screen = app.pygame.Surface((app.MENU_WIDTH, app.MENU_HEIGHT))
    app.draw_menu(
        screen,
        app.pygame.font.SysFont("segoeui", 30, bold=True),
        app.pygame.font.SysFont("segoeui", 24, bold=True),
        app.pygame.font.SysFont("segoeui", 18),
        custom_selected=True,
    )

    assert "Back" in labels
    assert "2 players" in labels
    assert "AI vs AI" in labels


def test_evaluation_bar_centers_even_position():
    app = _app()
    assert app.evaluation_fraction(0) == 0.5
    assert app.evaluation_label(0) == "even"


def test_evaluation_bar_tracks_x_and_o_advantage():
    app = _app()
    assert app.evaluation_fraction(100) > 0.5
    assert app.evaluation_fraction(-100) < 0.5
    assert app.evaluation_label(100) == "X 100"
    assert app.evaluation_label(-100) == "O 100"


@pytest.mark.parametrize("score", [-float("inf"), -1_000_000, 0, 1_000_000, float("inf")])
def test_evaluation_bar_stays_within_bounds(score):
    app = _app()
    fraction = app.evaluation_fraction(score)
    assert 0.0 <= fraction <= 1.0


def test_evaluation_bar_renders_current_board_evaluation():
    source = (STARTER_DIR / "app.py").read_text(encoding="utf-8")
    assert "raw = evaluate(board, PLAYER_X)" in source
    assert "normalized = evaluation_fraction(raw)" in source
    assert "draw_evaluation(screen, fonts, state.board)" in source


@pytest.mark.parametrize(
    "state_id",
    [
        "B1_open_start",
        "B2_depth_sensitive_block",
        "B3_alphabeta_reduction",
        "B4_full_column_failure",
    ],
)
def test_all_benchmarks_load_with_metadata_and_turn(state_id):
    app = _app()
    item = next(item for item in app.load_benchmarks() if item["id"] == state_id)
    state = app.benchmark_state(item)
    assert state.to_move == item["to_move"]
    assert state.board == ge.board_from_rows(item["board"])
    assert item["description"]


def test_loading_benchmark_resets_custom_board_size():
    app = _app()
    item = next(item for item in app.load_benchmarks() if item["id"] == "B1_open_start")
    ge.set_board_config(8, 9, 4)
    app.student_core_module.set_ai_board_config(8, 9, 4)

    state = app.benchmark_state(item)

    assert ge.ROWS == 6 and ge.COLUMNS == 7
    assert app.student_core_module.ROWS == 6 and app.student_core_module.COLUMNS == 7
    assert len(state.board) == 6 and len(state.board[0]) == 7


def test_b2_and_b4_benchmark_behaviors_are_preserved():
    app = _app()
    b2 = next(item for item in app.load_benchmarks() if item["id"].startswith("B2"))
    b4 = next(item for item in app.load_benchmarks() if item["id"].startswith("B4"))
    assert app.choose_ai_move(app.benchmark_state(b2), 2) == 3
    assert 3 not in ge.legal_moves(app.benchmark_state(b4).board)


def test_invalid_benchmark_metadata_is_rejected():
    app = _app()
    with pytest.raises(ValueError, match="missing fields"):
        app.benchmark_state({"id": "bad", "board": [], "to_move": ge.PLAYER_X})
    with pytest.raises(ValueError, match="Invalid benchmark player"):
        app.benchmark_state(
            {
                "id": "bad",
                "board": ["......."] * ge.ROWS,
                "to_move": "Z",
                "description": "bad",
            }
        )


def test_benchmark_ui_displays_description_without_key_hints():
    source = (STARTER_DIR / "app.py").read_text(encoding="utf-8")
    assert "draw_benchmark_info(screen, benchmark_item)" in source
    assert 'benchmarks[benchmark_index] if benchmark_index is not None else None' in source


def test_benchmark_details_draw_only_description(monkeypatch):
    app = _app()
    app.pygame.init()
    screen = app.pygame.Surface((app.GAME_WIDTH, app.GAME_HEIGHT))
    item = next(item for item in app.load_benchmarks() if item["id"] == "B2_depth_sensitive_block")
    rendered = []
    monkeypatch.setattr(app, "draw_text", lambda _screen, _font, text, *_args: rendered.append(text))

    app.draw_benchmark_details(screen, item)
    assert item["description"] in " ".join(rendered)
    assert not any(hint in " ".join(rendered) for hint in ("M:", "N:", "Space:", "To move:"))


def test_benchmark_compact_panel_only_shows_description(monkeypatch):
    app = _app()
    app.pygame.init()
    screen = app.pygame.Surface((app.GAME_WIDTH, app.GAME_HEIGHT))
    item = next(item for item in app.load_benchmarks() if item["id"] == "B4_full_column_failure")
    rendered = []
    monkeypatch.setattr(app, "draw_text", lambda _screen, _font, text, *_args: rendered.append(text))

    app.draw_benchmark_info(screen, item)
    joined = " ".join(rendered)
    assert item["description"].split()[0] in joined
    assert not any(hint in joined for hint in ("M:", "N:", "Space:", "I:"))


def test_ai_vs_ai_history_keyboard_shortcuts_include_n_and_m():
    source = (STARTER_DIR / "app.py").read_text(encoding="utf-8")
    assert "pygame.K_n" in source and "pygame.K_RIGHT" in source
    assert "pygame.K_m" in source and "pygame.K_LEFT" in source


def test_benchmark_loader_supports_pyinstaller_bundle_path():
    source = (STARTER_DIR / "app.py").read_text(encoding="utf-8")
    assert 'getattr(sys, "_MEIPASS", None)' in source
    assert 'Path(bundle_root) / "starter" / "sample_states.json"' in source


def test_window_can_resize_and_toggle_fullscreen():
    source = (STARTER_DIR / "app.py").read_text(encoding="utf-8")
    assert "pygame.RESIZABLE | pygame.SCALED" in source
    assert "pygame.K_F11" in source
    assert "pygame.display.toggle_fullscreen()" in source


def test_immediate_win_is_selected():
    app = _app()
    board = ge.board_from_rows(
        [
            ".......",
            ".......",
            ".......",
            ".......",
            ".......",
            "XXX.OO.",
        ]
    )
    state = ge.GameState(board, ge.PLAYER_X)
    assert app.choose_ai_move(state, 2) == 3


def test_opponent_fork_stress_state_returns_legal_move():
    app = _app()
    board = ge.board_from_rows(
        [
            ".......",
            ".......",
            ".......",
            "...O...",
            "..OXO..",
            ".XXOX..",
        ]
    )
    state = ge.GameState(board, ge.PLAYER_X)
    assert not state.is_terminal()
    assert app.choose_ai_move(state, 4) in ge.legal_moves(board)


def test_depth_seven_stress_move_is_legal():
    app = _app()
    state = app.benchmark_state(
        next(item for item in app.load_benchmarks() if item["id"] == "B3_alphabeta_reduction")
    )
    assert app.choose_ai_move(state, 7) in ge.legal_moves(state.board)


def test_stress_guards_are_present_in_application():
    source = (STARTER_DIR / "app.py").read_text(encoding="utf-8")
    assert "if state.is_terminal():" in source
    assert "if column not in legal_moves(state.board):" in source
    assert "except ValueError as exc:" in source
    assert "paused = True" in source
