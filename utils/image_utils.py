# utils/image_utils.py

import os
import io
import requests
from PIL import Image, ImageTk

# --------------------
# Session will be passed in or created externally
# --------------------

def download_stash_image(image_url, session, api_key=None):
    """
    Download an image from Stash, including API key authentication if needed.
    Returns bytes of the image.
    """
    headers = {}
    if api_key:
        headers["ApiKey"] = api_key  # Stash uses ApiKey header

    try:
        response = session.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            print(f"[image_utils] Warning: URL did not return an image. Content-Type: {content_type}")
            return None
        return response.content
    except Exception as e:
        print(f"[image_utils] Failed to download image: {e}")
        return None



def upload_file_to_hamster(file_path, api_key: str, upload_url: str):
    """Upload a file to HamsterImg and return the URL"""
    try:
        with open(file_path, 'rb') as f:
            files = {'source': (os.path.basename(file_path), f, 'image/jpeg')}
            headers = {'X-API-Key': api_key}

            r = requests.post(upload_url, headers=headers, files=files, timeout=30)
            r.raise_for_status()

            result = r.json()
            if result.get('status_code') == 200:
                return result['image']['url']
            return None

    except Exception as e:
        print(f"[image_utils] Upload error: {e}")
        return None


def upload_image_data_to_hamster(image_data, api_key: str, upload_url: str, filename="image.jpg"):
    """Upload image data to HamsterImg and return the URL"""
    try:
        files = {'source': (filename, image_data, 'image/jpeg')}
        headers = {'X-API-Key': api_key}

        r = requests.post(upload_url, headers=headers, files=files, timeout=30)
        r.raise_for_status()

        result = r.json()
        if result.get('status_code') == 200:
            return result['image']['url']
        return None

    except Exception as e:
        print(f"[image_utils] Upload error: {e}")
        return None


def build_image_url(image_path, base_url="http://192.168.1.109:9999"):
    """Build complete image URL, handling both relative and absolute paths"""
    if not image_path:
        return None

    if image_path.startswith("http://") or image_path.startswith("https://"):
        return image_path

    if image_path.startswith("/"):
        return f"{base_url}{image_path}"
    return f"{base_url}/{image_path}"


def format_duration(seconds):
    """Format seconds into HH:MM:SS or MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


# --------------------
# Image Display
# --------------------
def display_image(image_data, label_widget, max_width=280, max_height=280):
    """Display image in a Tkinter label, resizing to max dimensions"""
    try:
        if not image_data:
            label_widget.configure(image="", text="No image data")
            return False

        img = Image.open(io.BytesIO(image_data))
        img.thumbnail(
            (max_width, max_height),
            Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS
        )

        photo = ImageTk.PhotoImage(img)
        label_widget.configure(image=photo, text="")
        label_widget.image = photo  # Keep reference to avoid GC
        return True

    except Exception as e:
        print(f"Image display error: {e}")
        label_widget.configure(image="", text="Failed to display")
        return False
