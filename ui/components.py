import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


DEFAULT_FONT_PATH = "C:/Windows/Fonts/segoeui.ttf"
DEFAULT_BOLD_FONT_PATH = "C:/Windows/Fonts/segoeuib.ttf"
_FONT_CACHE = {}
_CANVAS_CACHE = {}


def _get_font(size: int, font_path: str = DEFAULT_FONT_PATH):
    cache_key = (font_path, size)

    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]

    try:
        font = ImageFont.truetype(font_path, size)
    except Exception:
        font = ImageFont.load_default()

    _FONT_CACHE[cache_key] = font
    return font


def _scale_to_font_size(scale: float | None) -> int:
    if scale is None:
        return 26

    return max(14, int(scale * 28))


def draw_text(
    image,
    text: str,
    position: tuple[int, int],
    scale: float | None = None,
    color: tuple[int, int, int] = (255, 255, 255),
    thickness: int = 1,
    font_size: int | None = None,
    font_path: str = DEFAULT_FONT_PATH,
):
    if font_size is None:
        font_size = _scale_to_font_size(scale)

    try:
        text.encode("ascii")
        is_ascii = True
    except UnicodeEncodeError:
        is_ascii = False

    if is_ascii:
        cv_scale = max(0.45, font_size / 30.0)
        cv2.putText(
            image,
            text,
            position,
            cv2.FONT_HERSHEY_SIMPLEX,
            cv_scale,
            color,
            max(1, thickness),
            cv2.LINE_AA,
        )
        return

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(image_rgb)
    draw = ImageDraw.Draw(pil_img)
    font = _get_font(font_size, font_path=font_path)
    rgb_color = (color[2], color[1], color[0])
    draw.text(position, text, font=font, fill=rgb_color)
    image[:] = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def draw_text_centered(
    image,
    text: str,
    rect: tuple[int, int, int, int],
    font_size: int = 18,
    color: tuple[int, int, int] = (255, 255, 255),
    font_path: str = DEFAULT_FONT_PATH,
):
    x, y, w, h = rect

    try:
        text.encode("ascii")
        is_ascii = True
    except UnicodeEncodeError:
        is_ascii = False

    if is_ascii:
        cv_scale = max(0.45, font_size / 30.0)
        thickness = 1
        (text_w, text_h), baseline = cv2.getTextSize(
            text,
            cv2.FONT_HERSHEY_SIMPLEX,
            cv_scale,
            thickness,
        )
        text_x = x + max(0, (w - text_w) // 2)
        text_y = y + max(text_h, (h + text_h) // 2 - baseline)
        cv2.putText(
            image,
            text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            cv_scale,
            color,
            thickness,
            cv2.LINE_AA,
        )
        return

    draw_text(
        image,
        text,
        (x + 10, y + h // 2),
        font_size=font_size,
        color=color,
        font_path=font_path,
    )


def _fit_ascii_text(text: str, font_size: int, max_width: int) -> str:
    if max_width <= 0:
        return text

    cv_scale = max(0.45, font_size / 30.0)
    thickness = 1

    fitted = text
    while fitted:
        text_width = cv2.getTextSize(fitted, cv2.FONT_HERSHEY_SIMPLEX, cv_scale, thickness)[0][0]
        if text_width <= max_width:
            return fitted
        fitted = fitted[:-1]

    return text


def draw_panel(
    image,
    x: int,
    y: int,
    w: int,
    h: int,
    bg_color: tuple[int, int, int] = (25, 25, 25),
    border_color: tuple[int, int, int] = (70, 70, 70),
    border_thickness: int = 2,
    shadow: bool = True,
):
    if shadow:
        cv2.rectangle(image, (x + 4, y + 6), (x + w + 4, y + h + 6), (8, 8, 8), -1)
    cv2.rectangle(image, (x, y), (x + w, y + h), bg_color, -1)
    if border_thickness > 0:
        cv2.rectangle(image, (x, y), (x + w, y + h), border_color, border_thickness)


def draw_button(
    image,
    rect: tuple[int, int, int, int],
    title: str,
    subtitle: str = "",
    is_hovered: bool = False,
    is_active: bool = False,
    accent_color: tuple[int, int, int] = (82, 163, 255),
    badge_text: str | None = None,
):
    x, y, w, h = rect

    if is_active:
        bg_color = (48, 64, 92)
        border_color = accent_color
    elif is_hovered:
        bg_color = (34, 43, 60)
        border_color = (108, 137, 188)
    else:
        bg_color = (28, 32, 38)
        border_color = (66, 74, 86)

    draw_panel(
        image,
        x,
        y,
        w,
        h,
        bg_color=bg_color,
        border_color=border_color,
        border_thickness=2,
    )

    cv2.rectangle(image, (x + 12, y + 12), (x + 20, y + max(20, h - 12)), accent_color, -1)

    title_size = max(17, min(26, int(h * 0.22)))
    subtitle_size = max(12, min(16, int(h * 0.14)))
    title_y = y + 28
    subtitle_y = y + 58

    draw_text(
        image,
        title,
        (x + 34, title_y),
        font_size=title_size,
        color=(255, 255, 255),
        font_path=DEFAULT_BOLD_FONT_PATH,
    )

    if subtitle:
        draw_text(
            image,
            subtitle,
            (x + 34, subtitle_y),
            font_size=subtitle_size,
            color=(208, 214, 224),
        )

    if badge_text:
        badge_w = max(64, 22 + len(badge_text) * 12)
        badge_h = 34
        badge_x = x + w - badge_w - 18
        badge_y = y + 16

        cv2.rectangle(image, (badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h), accent_color, -1)
        draw_text_centered(
            image,
            badge_text,
            (badge_x, badge_y, badge_w, badge_h),
            font_size=17,
            color=(255, 255, 255),
            font_path=DEFAULT_BOLD_FONT_PATH,
        )


def draw_top_bar(image, title: str, subtitle: str = ""):
    height, width = image.shape[:2]
    bar_h = max(104, int(height * 0.14))

    for row in range(bar_h):
        blend = row / max(1, bar_h - 1)
        color = (
            int(34 + 10 * blend),
            int(24 + 14 * blend),
            int(16 + 22 * blend),
        )
        cv2.line(image, (0, row), (width, row), color, 1)

    cv2.line(image, (0, bar_h - 1), (width, bar_h - 1), (90, 110, 150), 2)

    draw_text(
        image,
        title,
        (28, 18),
        font_size=34,
        color=(255, 255, 255),
        font_path=DEFAULT_BOLD_FONT_PATH,
    )

    if subtitle:
        draw_text(
            image,
            subtitle,
            (30, 62),
            font_size=18,
            color=(217, 221, 228),
        )

    return bar_h


def point_in_rect(point: tuple[int, int], rect: tuple[int, int, int, int]) -> bool:
    px, py = point
    x, y, w, h = rect
    return x <= px <= x + w and y <= py <= y + h


def draw_pointer(image, point: tuple[int, int], color=(0, 255, 255)):
    x, y = point
    cv2.circle(image, (x, y), 22, color, 2)
    cv2.circle(image, (x, y), 11, color, -1)
    cv2.circle(image, (x, y), 4, (255, 255, 255), -1)


def draw_hand_status_badge(image, x: int, y: int, label: str, gesture: str):
    w, h = 200, 58
    font_size = 14
    text = _fit_ascii_text(f"{label}: {gesture}", font_size=font_size, max_width=w - 22)
    draw_panel(image, x, y, w, h, bg_color=(30, 34, 40), border_color=(76, 84, 96), border_thickness=2)

    draw_text_centered(
        image,
        text,
        (x, y, w, h),
        font_size=font_size,
        color=(255, 255, 255),
    )


def get_hand_badge_positions(x: int, y: int, available_w: int, count: int, badge_w: int = 200, gap: int = 12):
    positions = []
    if count <= 0:
        return positions

    total_w = count * badge_w + (count - 1) * gap
    if count > 1 and total_w <= available_w:
        for idx in range(count):
            positions.append((x + idx * (badge_w + gap), y))
        return positions

    for idx in range(count):
        positions.append((x, y + idx * 66))
    return positions


def draw_icon_dot(image, x: int, y: int, color=(0, 255, 0), radius: int = 8):
    cv2.circle(image, (x, y), radius, color, -1)
    cv2.circle(image, (x, y), radius + 3, color, 2)


def create_app_canvas(width: int, height: int, bg_color=(10, 10, 10)):
    cache_key = (width, height, bg_color)
    cached = _CANVAS_CACHE.get(cache_key)
    if cached is not None:
        return cached.copy()

    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    top = np.array((18, 20, 28), dtype=np.float32)
    bottom = np.array(bg_color, dtype=np.float32)
    gradient = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None]
    colors = (top * (1.0 - gradient) + bottom * gradient).astype(np.uint8)
    canvas[:] = colors[:, None, :]

    _CANVAS_CACHE[cache_key] = canvas.copy()
    return canvas


def draw_text_lines(
    image,
    lines: list[str],
    start_position: tuple[int, int],
    line_height: int = 28,
    font_size: int = 18,
    color: tuple[int, int, int] = (255, 255, 255),
    font_path: str = DEFAULT_FONT_PATH,
):
    x, y = start_position
    for line in lines:
        draw_text(
            image,
            line,
            (x, y),
            font_size=font_size,
            color=color,
            font_path=font_path,
        )
        y += line_height
