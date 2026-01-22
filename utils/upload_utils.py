# utils/upload_utils.py
import os
import tempfile
from tkinter import messagebox
from utils.ffmpeg_utils import generate_contact_sheet, generate_individual_screens
from utils.image_utils import upload_file_to_hamster, upload_image_data_to_hamster, download_stash_image, build_image_url
from paths.path_mapper import load_path_mappings, map_path

def generate_and_upload(current_scene_data, studio_image_data, performer_images_data, title_var, hamster_api_key, hamster_upload_url, stash_session):
    """
    Generates contact sheet and screenshots, uploads to Hamster,
    stores URLs in current_scene_data, and returns a list of BBCode image links.
    """
    if not current_scene_data.get("files"):
        messagebox.showerror("Error", "No video file found")
        return []
    
    video_file = current_scene_data['files'][0]
    linux_path = video_file.get('path')
    path_mappings = load_path_mappings()
    video_path = map_path(linux_path, path_mappings)
    
    if not os.path.exists(video_path):
        messagebox.showerror("Error", f"Video file not found: {video_path}")
        return []
    
    temp_dir = tempfile.mkdtemp()
    contact_sheet_path = os.path.join(temp_dir, "contactsheet.jpg")
    screens_dir = os.path.join(temp_dir, "screens")
    os.makedirs(screens_dir, exist_ok=True)
    
    generate_contact_sheet(
        video_path,
        contact_sheet_path,
        title_var.get(),
        video_file.get("duration", 0),
        f"{video_file.get('width',0)}x{video_file.get('height',0)}"
    )
    
    screen_files = generate_individual_screens(video_path, screens_dir, video_file.get("duration",0))
    
    # Upload studio image
    if studio_image_data.get("data"):
        studio_image_data["url"] = upload_image_data_to_hamster(
            studio_image_data["data"], hamster_api_key, hamster_upload_url, "studio.jpg"
        )
    
    # Upload performer images
    for perf in performer_images_data:
        perf["url"] = upload_image_data_to_hamster(
            perf["data"], hamster_api_key, hamster_upload_url, f"{perf['name']}.jpg"
        )
    
    # Upload poster/cover image
    poster_url = None
    print(f"[upload_utils] Looking for poster in scene data...")
    print(f"[upload_utils] Scene data keys: {current_scene_data.keys()}")
    
    # Try multiple possible locations for the screenshot/poster
    screenshot_path = None
    
    # Method 1: paths.screenshot
    if current_scene_data.get('paths', {}).get('screenshot'):
        screenshot_path = current_scene_data['paths']['screenshot']
        print(f"[upload_utils] Found screenshot in paths.screenshot: {screenshot_path}")
    
    # Method 2: Direct screenshot key
    elif current_scene_data.get('screenshot'):
        screenshot_path = current_scene_data['screenshot']
        print(f"[upload_utils] Found screenshot in direct key: {screenshot_path}")
    
    # Method 3: image_path key
    elif current_scene_data.get('image_path'):
        screenshot_path = current_scene_data['image_path']
        print(f"[upload_utils] Found screenshot in image_path: {screenshot_path}")
    
    # Method 4: Check if there's a cover image
    elif current_scene_data.get('cover_image'):
        screenshot_path = current_scene_data['cover_image']
        print(f"[upload_utils] Found screenshot in cover_image: {screenshot_path}")
    
    if screenshot_path:
        poster_image_url = build_image_url(screenshot_path)
        print(f"[upload_utils] Poster URL: {poster_image_url}")
        poster_data = download_stash_image(poster_image_url, stash_session)
        if poster_data:
            print(f"[upload_utils] Downloaded poster data: {len(poster_data)} bytes")
            poster_url = upload_image_data_to_hamster(
                poster_data, hamster_api_key, hamster_upload_url, "poster.jpg"
            )
            print(f"[upload_utils] Poster uploaded: {poster_url}")
        else:
            print(f"[upload_utils] Failed to download poster from {poster_image_url}")
    else:
        print(f"[upload_utils] No screenshot path found. Available keys: {list(current_scene_data.keys())}")
    
    if not poster_url:
        print(f"[upload_utils] Warning: No poster uploaded.")
    
    # Upload contact sheet and individual screens
    contact_url = upload_file_to_hamster(contact_sheet_path, hamster_api_key, hamster_upload_url)
    screen_urls = [upload_file_to_hamster(f, hamster_api_key, hamster_upload_url) for f in screen_files]
    
    # Store URLs in current_scene_data for the new BBCode generator
    current_scene_data['contact_sheet_url'] = contact_url
    current_scene_data['screenshot_urls'] = [url for url in screen_urls if url]  # Filter out None values
    current_scene_data['poster_url'] = poster_url
    
    # Build BBCode (legacy format)
    bbcode_lines = []
    if studio_image_data.get("url"):
        bbcode_lines.append(f"[img]{studio_image_data['url']}[/img]")
    
    for perf in performer_images_data:
        if perf.get("url"):
            bbcode_lines.append(f"[img]{perf['url']}[/img]")
    
    if poster_url:
        bbcode_lines.append(f"[img]{poster_url}[/img]")
    
    if contact_url:
        bbcode_lines.append(f"[img]{contact_url}[/img]")
    
    for url in screen_urls:
        if url:
            bbcode_lines.append(f"[img]{url}[/img]")
    
    messagebox.showinfo("Success", "Images generated and uploaded successfully!")
    return bbcode_lines