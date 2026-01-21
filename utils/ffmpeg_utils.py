# utils/ffmpeg_utils.py

import os
import tempfile
import subprocess
from PIL import Image, ImageDraw, ImageFont

from config import CONTACT_ROWS, CONTACT_COLS, THUMB_WIDTH, THUMB_HEIGHT, CONTACT_HEADER_HEIGHT
from utils.image_utils import format_duration

# --------------------
# Contact Sheet
# --------------------
def generate_contact_sheet(video_path, output_path, title, duration, dimensions):
    ROWS = CONTACT_ROWS
    COLS = CONTACT_COLS
    THUMB_W = THUMB_WIDTH
    THUMB_H = THUMB_HEIGHT
    HEADER_H = CONTACT_HEADER_HEIGHT

    if not os.path.exists(video_path):
        print(f"Video file does not exist: {video_path}")
        return False

    total_thumbs = ROWS * COLS
    frame_files = []

    try:
        temp_dir = tempfile.mkdtemp()
        safe_duration = max(duration, total_thumbs + 1)

        for i in range(total_thumbs):
            timestamp = (safe_duration / (total_thumbs + 1)) * (i + 1)
            frame_path = os.path.join(temp_dir, f"frame_{i:02d}.jpg")

            cmd = [
                "ffmpeg", "-y",
                "-ss", f"{timestamp:.3f}",
                "-i", video_path,
                "-frames:v", "1",
                "-vf", f"scale={THUMB_W}:{THUMB_H}",
                frame_path
            ]

            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0 and os.path.exists(frame_path):
                frame_files.append(frame_path)
            else:
                print(f"Frame {i+1} failed: {result.stderr.strip()}")

        if not frame_files:
            print("No frames generated")
            return False

        contact_width = THUMB_W * COLS
        contact_height = (THUMB_H * ROWS) + HEADER_H
        contact = Image.new("RGB", (contact_width, contact_height), "black")
        draw = ImageDraw.Draw(contact)

        try:
            font_title = ImageFont.truetype("arial.ttf", 16)
            font_info = ImageFont.truetype("arial.ttf", 12)
        except Exception:
            font_title = ImageFont.load_default()
            font_info = ImageFont.load_default()

        # Header
        draw.rectangle((0, 0, contact_width, HEADER_H), fill="white")
        draw.text((10, 10), title or "Untitled", fill="black", font=font_title)
        draw.text((10, 35), f"Duration: {format_duration(duration)}", fill="black", font=font_info)
        draw.text((10, 55), f"Dimensions: {dimensions}", fill="black", font=font_info)

        for idx, frame_path in enumerate(frame_files):
            row = idx // COLS
            col = idx % COLS
            x = col * THUMB_W
            y = HEADER_H + (row * THUMB_H)
            with Image.open(frame_path) as thumb:
                contact.paste(thumb, (x, y))

        contact.save(output_path, "JPEG", quality=95)
        print(f"Contact sheet saved: {output_path}")
        return True

    finally:
        for f in frame_files:
            try: os.remove(f)
            except: pass
        try: os.rmdir(temp_dir)
        except: pass


# --------------------
# Individual Screens
# --------------------
def generate_individual_screens(video_path, output_dir, duration, count=10):
    if not os.path.exists(video_path):
        print(f"Video file does not exist: {video_path}")
        return []

    os.makedirs(output_dir, exist_ok=True)
    screen_files = []
    safe_duration = max(duration, count + 1)
    interval = safe_duration / (count + 1)

    for i in range(1, count + 1):
        timestamp = interval * i
        output_file = os.path.join(output_dir, f"screen_{i:02d}.jpg")
        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{timestamp:.3f}",
            "-i", video_path,
            "-frames:v", "1",
            "-vf", "scale=1920:-1",
            output_file
        ]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0 and os.path.exists(output_file):
            screen_files.append(output_file)
        else:
            print(f"Screen {i} failed: {result.stderr.strip()}")
    return screen_files
