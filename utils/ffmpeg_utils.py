import os
import tempfile
import subprocess
from PIL import Image, ImageDraw, ImageFont

from config import CONTACT_ROWS, CONTACT_COLS, THUMB_WIDTH, THUMB_HEIGHT, CONTACT_HEADER_HEIGHT
from utils.image_utils import format_duration

# --------------------
# Contact Sheet - FAST method
# --------------------
def generate_contact_sheet(video_path, output_path, title, duration, dimensions):
    """
    Generate contact sheet - tries vcsi first, then fast FFmpeg batch extraction.
    """
    ROWS = CONTACT_ROWS
    COLS = CONTACT_COLS

    if not os.path.exists(video_path):
        print(f"Video file does not exist: {video_path}")
        return False

    try:
        # Try using vcsi first (most reliable)
        layout = f"{COLS}x{ROWS}"
        cmd = [
            "vcsi",
            video_path,
            "-g", layout,
            "-o", output_path,
            "--metadata-font-size", "16",
            "--timestamp-font-size", "12"
        ]
        
        print(f"[ffmpeg_utils] Running vcsi: {' '.join(cmd)}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"Contact sheet saved using vcsi: {output_path}")
            return True
        else:
            print("vcsi failed, falling back to FFmpeg method")
            return generate_contact_sheet_ffmpeg_fast(video_path, output_path, title, duration, dimensions)
            
    except FileNotFoundError:
        print("vcsi not found, using FFmpeg method")
        return generate_contact_sheet_ffmpeg_fast(video_path, output_path, title, duration, dimensions)


# --------------------
# Contact Sheet using FFmpeg - FAST batch extraction
# --------------------
def generate_contact_sheet_ffmpeg_fast(video_path, output_path, title, duration, dimensions):
    """
    Generate contact sheet using FFmpeg with FAST batch frame extraction.
    Extracts all frames in a single FFmpeg call using fps filter.
    """
    ROWS = CONTACT_ROWS
    COLS = CONTACT_COLS
    THUMB_W = THUMB_WIDTH
    THUMB_H = THUMB_HEIGHT
    HEADER_H = CONTACT_HEADER_HEIGHT

    total_thumbs = ROWS * COLS
    frame_files = []

    try:
        temp_dir = tempfile.mkdtemp()
        safe_duration = max(duration, total_thumbs + 1)
        
        frame_pattern = os.path.join(temp_dir, "frame_%02d.jpg")
        
        # Calculate the fps needed to get exactly total_thumbs frames
        # We want frames evenly distributed across the video
        fps = total_thumbs / safe_duration
        
        # FAST METHOD: Extract all frames in ONE ffmpeg call using fps filter
        # -ss before -i for speed, fps filter for even distribution
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", f"fps={fps},scale={THUMB_W}:{THUMB_H}:force_original_aspect_ratio=decrease",
            "-vframes", str(total_thumbs),
            "-q:v", "2",
            frame_pattern
        ]
        
        print(f"[ffmpeg_utils] Extracting {total_thumbs} frames in one pass (fps={fps:.4f})...")
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            # Collect generated frames
            for i in range(total_thumbs):
                frame_path = os.path.join(temp_dir, f"frame_{i+1:02d}.jpg")
                if os.path.exists(frame_path):
                    frame_files.append(frame_path)
            print(f"[ffmpeg_utils] Successfully extracted {len(frame_files)} frames")
        else:
            print(f"Batch extraction failed: {result.stderr}")
            return False

        if not frame_files:
            print("No frames generated")
            return False

        # Create contact sheet image
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

        # Calculate file size
        file_size_bytes = os.path.getsize(video_path)
        file_size_gb = file_size_bytes / (1024**3)
        
        # Header
        draw.rectangle((0, 0, contact_width, HEADER_H), fill="white")
        draw.text((10, 10), title or "Untitled", fill="black", font=font_title)
        draw.text((10, 35), f"Duration: {format_duration(duration)}", fill="black", font=font_info)
        draw.text((10, 55), f"Dimensions: {dimensions}", fill="black", font=font_info)
        draw.text((10, 75), f"Filesize: {file_size_gb:.2f}gb", fill="black", font=font_info)

        # Paste thumbnails
        for idx, frame_path in enumerate(frame_files):
            row = idx // COLS
            col = idx % COLS
            x = col * THUMB_W
            y = HEADER_H + (row * THUMB_H)
            
            try:
                with Image.open(frame_path) as thumb:
                    # If image is smaller than thumb size, center it
                    if thumb.size[0] < THUMB_W or thumb.size[1] < THUMB_H:
                        bg = Image.new("RGB", (THUMB_W, THUMB_H), "black")
                        x_offset = (THUMB_W - thumb.size[0]) // 2
                        y_offset = (THUMB_H - thumb.size[1]) // 2
                        bg.paste(thumb, (x_offset, y_offset))
                        contact.paste(bg, (x, y))
                    else:
                        contact.paste(thumb, (x, y))
            except Exception as e:
                print(f"Error pasting frame {idx}: {e}")

        contact.save(output_path, "JPEG", quality=95)
        print(f"Contact sheet saved: {output_path}")
        return True

    except Exception as e:
        print(f"Error generating contact sheet: {e}")
        return False
    finally:
        for f in frame_files:
            try: os.remove(f)
            except: pass
        try: os.rmdir(temp_dir)
        except: pass


# --------------------
# Individual Screens - FAST method
# --------------------
def generate_individual_screens(video_path, output_dir, duration, count=12):
    """
    Generate individual screenshots quickly using -ss before -i.
    Uses offset timestamps to avoid duplicating contact sheet frames.
    """
    if not os.path.exists(video_path):
        print(f"Video file does not exist: {video_path}")
        return []

    os.makedirs(output_dir, exist_ok=True)
    screen_files = []
    safe_duration = max(duration, count + 1)
    
    # Offset by half interval to avoid contact sheet frames
    interval = safe_duration / (count + 1)
    offset = interval * 0.5
    
    for i in range(1, count + 1):
        timestamp = (interval * i) + offset
        timestamp = min(timestamp, safe_duration - 1)
        
        output_file = os.path.join(output_dir, f"screen_{i:02d}.jpg")
        
        # FAST: -ss BEFORE -i for speed
        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{timestamp:.3f}",
            "-i", video_path,
            "-vframes", "1",
            "-vf", "scale=1920:-1",
            "-q:v", "2",
            output_file
        ]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0 and os.path.exists(output_file):
            screen_files.append(output_file)
            print(f"[ffmpeg_utils] Screen {i} generated at {timestamp:.2f}s")
        else:
            print(f"Screen {i} failed")
    
    print(f"[ffmpeg_utils] Generated {len(screen_files)} individual screens")
    return screen_files


# --------------------
# Generate video thumbnail
# --------------------
def generate_video_thumbnail(video_path, time_sec=30, width=300):
    """
    Generate a single-frame thumbnail from a video using ffmpeg.
    Returns the path to the thumbnail file.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    fd, thumb_path = tempfile.mkstemp(suffix="-thumbnail.jpg")
    os.close(fd)

    # FAST: -ss before -i
    cmd = [
        "ffmpeg",
        "-ss", str(time_sec),
        "-i", video_path,
        "-vf", f"scale={width}:-1",
        "-vframes", "1",
        "-q:v", "2",
        "-y",
        thumb_path
    ]

    print(f"[ffmpeg_utils] Running ffmpeg command: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    if not os.path.exists(thumb_path):
        raise RuntimeError(f"Thumbnail was not created: {thumb_path}")

    return thumb_path