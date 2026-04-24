import ui.menu_screen as menu_module
from ui.menu_screen import MenuScreen


def test_menu_selection_waits_for_countdown(monkeypatch):
    now = 100.0
    monkeypatch.setattr(menu_module.time, "monotonic", lambda: now)

    screen = MenuScreen(countdown_seconds=3.0)
    screen.hovered_item_index = 0

    assert screen.try_select("PINCH") is None
    assert screen.try_select("PINCH") is None

    now = 103.0
    assert screen.try_select("PINCH") == "drawing"


def test_menu_selection_requires_holding_pinch_for_full_countdown(monkeypatch):
    now = 100.0
    monkeypatch.setattr(menu_module.time, "monotonic", lambda: now)

    screen = MenuScreen(countdown_seconds=3.0)
    screen.hovered_item_index = 0

    assert screen.try_select("PINCH") is None

    now = 101.5
    assert screen.try_select("UNKNOWN") is None

    screen.hovered_item_index = 0
    now = 104.6
    assert screen.try_select("PINCH") is None


def test_menu_selection_cancels_when_hover_moves_off_pending_item(monkeypatch):
    now = 100.0
    monkeypatch.setattr(menu_module.time, "monotonic", lambda: now)

    screen = MenuScreen(countdown_seconds=3.0)
    screen.hovered_item_index = 0

    assert screen.try_select("PINCH") is None

    screen.hovered_item_index = 1
    now = 101.0
    assert screen.try_select("PINCH") is None

    now = 104.1
    assert screen.try_select("PINCH") is None


def test_menu_rects_fit_inside_panel():
    screen = MenuScreen(countdown_seconds=3.0)
    layout = screen._build_layout(app_width=1400, app_height=900)
    rects = screen._build_menu_rects(layout["right_panel"])

    _, panel_y, _, panel_h = layout["right_panel"]
    panel_bottom = panel_y + panel_h
    last_rect = rects[-1]
    last_bottom = last_rect[1] + last_rect[3]

    assert len(rects) == len(screen.menu_items)
    assert last_bottom <= panel_bottom
