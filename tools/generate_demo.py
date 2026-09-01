"""Generate the visual assets used by the GitHub landing page.

This is a deterministic, offline renderer for a product teaser.  It mirrors
the app's dark desktop + amber accretion-disk visual language without needing
an interactive OpenGL desktop during documentation builds.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WIDTH, HEIGHT = 720, 405
FRAME_COUNT, FPS = 42, 12


def font(size: int, mono: bool = False):
    candidates = (
        [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\cour.ttf"]
        if mono
        else [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]
    )
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def background() -> np.ndarray:
    """Create a fake dark code-editor desktop for the lensing effect."""
    y, x = np.mgrid[0:HEIGHT, 0:WIDTH]
    grad = np.clip(1.0 - y / HEIGHT, 0, 1)
    arr = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)
    arr[..., 0] = 9 + 9 * grad
    arr[..., 1] = 12 + 12 * grad
    arr[..., 2] = 25 + 28 * grad

    image = Image.fromarray(np.uint8(np.clip(arr, 0, 255)), "RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, 0, WIDTH, 34), fill=(18, 22, 40, 255))
    draw.ellipse((15, 12, 23, 20), fill=(255, 95, 90, 220))
    draw.ellipse((28, 12, 36, 20), fill=(255, 190, 70, 220))
    draw.ellipse((41, 12, 49, 20), fill=(90, 215, 125, 220))
    draw.text((68, 8), "Blackhole Eye Care  /  demo", fill=(190, 198, 220, 210), font=font(14))

    code = [
        ("def protect_your_eyes():", (110, 210, 188)),
        ("    while working:", (198, 165, 255)),
        ("        if timer.minutes >= 20:", (198, 165, 255)),
        ("            summon_black_hole()", (255, 188, 105)),
        ("            wait_for_a_real_break()", (255, 188, 105)),
        ("        sleep(1)", (155, 170, 205)),
        ("# your screen is not a replacement for a break", (90, 112, 145)),
    ]
    for idx, (line, color) in enumerate(code):
        draw.text((42, 76 + idx * 35), line, fill=(*color, 235), font=font(18, mono=True))

    draw.rounded_rectangle((42, HEIGHT - 49, WIDTH - 42, HEIGHT - 20), radius=8, fill=(25, 31, 56, 230))
    draw.text((56, HEIGHT - 45), "WORKING", fill=(100, 220, 166, 235), font=font(12, mono=True))
    draw.text((WIDTH - 177, HEIGHT - 45), "next reminder  20:00", fill=(155, 170, 205, 210), font=font(12, mono=True))
    return np.asarray(image).astype(np.float32)


def render(base: np.ndarray, frame: int) -> Image.Image:
    t = frame / (FRAME_COUNT - 1)
    # Ease in, pause at full scale, then shrink into a seamless loop.
    loop_t = (t * 1.18) % 1.0
    growth = 1 / (1 + math.exp(-8 * (loop_t - 0.47)))
    growth = 0.04 + 0.96 * growth
    cx = 0.53 + 0.035 * math.sin(loop_t * math.tau * 1.2)
    cy = 0.47 + 0.025 * math.cos(loop_t * math.tau * 0.9)
    px, py = cx * WIDTH, cy * HEIGHT
    yy, xx = np.mgrid[0:HEIGHT, 0:WIDTH]
    dx = (xx - px) / HEIGHT
    dy = (yy - py) / HEIGHT
    dist = np.sqrt(dx * dx + dy * dy)
    angle = np.arctan2(dy, dx)

    # Gravitational lens approximation: pull nearby pixels around the shadow.
    radius = 0.075 + 0.145 * growth
    influence = np.clip((radius * 2.25 - dist) / (radius * 2.25), 0, 1)
    bend = influence**2 * (0.12 + 0.18 * growth)
    source_r = dist + bend * radius
    source_a = angle + bend * (0.55 + 1.25 * growth)
    sx = np.clip(np.rint(px + np.cos(source_a) * source_r * HEIGHT), 0, WIDTH - 1).astype(int)
    sy = np.clip(np.rint(py + np.sin(source_a) * source_r * HEIGHT), 0, HEIGHT - 1).astype(int)
    warped = base[sy, sx].copy()

    # Warm relativistic disk and blue-white photon ring.
    disk_r = dist / np.maximum(radius, 1e-5)
    disk = np.exp(-((disk_r - 1.18) / 0.23) ** 2) * np.clip(growth * 1.35, 0, 1)
    streaks = 0.55 + 0.45 * np.sin(angle * 10 - loop_t * math.tau * 3 + disk_r * 8)
    disk *= np.clip(streaks, 0, 1)
    disk_color = np.stack((255 * disk, 128 * disk + 50 * disk**2, 30 * disk + 12 * disk**2), axis=-1)
    warped = np.clip(warped + disk_color, 0, 255)

    ring = np.exp(-((disk_r - 0.98) / 0.055) ** 2) * (0.28 + 0.72 * growth)
    warped += np.stack((90 * ring, 170 * ring, 255 * ring), axis=-1)

    shadow = np.clip((0.73 - disk_r) * 6, 0, 1)
    warped *= (1 - shadow[..., None] * 0.98)

    # A soft vignette keeps the focus on the effect.
    vignette = 1 - 0.32 * np.clip(((xx - WIDTH / 2) / WIDTH) ** 2 + ((yy - HEIGHT / 2) / HEIGHT) ** 2, 0, 1)
    warped *= vignette[..., None]
    image = Image.fromarray(np.uint8(np.clip(warped, 0, 255)), "RGB")

    # Add a crisp product label above the warped desktop.
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.rounded_rectangle((WIDTH - 239, 48, WIDTH - 31, 83), radius=10, fill=(10, 12, 25, 185), outline=(255, 180, 95, 150), width=1)
    draw.text((WIDTH - 218, 57), "REST  /  black hole active", fill=(255, 205, 130, 235), font=font(13, mono=True))
    image = Image.alpha_composite(image.convert("RGBA"), overlay)
    return image.convert("P", palette=Image.Palette.ADAPTIVE, colors=192)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    base = background()
    frames = [render(base, index) for index in range(FRAME_COUNT)]
    frames[0].save(ASSETS / "demo.gif", save_all=True, append_images=frames[1:], duration=round(1000 / FPS), loop=0, optimize=True, disposal=2)

    # Social Preview is 2:1 (1280x640).  Use the strongest frame plus a title card.
    hero = frames[24].convert("RGB").resize((1280, 720), Image.Resampling.LANCZOS)
    cover = Image.new("RGB", (1280, 640), (8, 10, 22))
    # Crop the editor chrome out of the social card so the title is the first
    # thing a visitor sees when GitHub renders the preview.
    cover.paste(hero.crop((0, 80, 1280, 720)), (0, 0))
    cover = cover.filter(ImageFilter.GaussianBlur(0.15))
    draw = ImageDraw.Draw(cover, "RGBA")
    draw.rectangle((0, 0, 1280, 640), fill=(5, 8, 20, 82))
    draw.rounded_rectangle((70, 76, 770, 300), radius=24, fill=(8, 12, 28, 220), outline=(255, 178, 91, 170), width=2)
    draw.text((112, 116), "BLACKHOLE", fill=(255, 200, 125, 255), font=font(67))
    draw.text((112, 190), "EYE CARE", fill=(236, 240, 255, 255), font=font(67))
    draw.text((116, 274), "A beautiful reminder to look away.", fill=(196, 207, 235, 235), font=font(24))
    cover.save(ASSETS / "social-preview.png", optimize=True)
    print(f"Generated {ASSETS / 'demo.gif'} and {ASSETS / 'social-preview.png'}")


if __name__ == "__main__":
    main()

