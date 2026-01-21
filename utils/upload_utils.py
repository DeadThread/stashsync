# utils/upload_utils.py
import os
import tempfile
from tkinter import messagebox
from utils.ffmpeg_utils import generate_contact_sheet, generate_individual_screens
from utils.image_utils import upload_file_to_hamster, upload_image_data_to_hamster
from paths.path_mapper import load_path_mappings, map_path

def generate_and_upload(current_scene_data, studio_image_data, performer_images_data, title_var, hamster_api_key, hamster_upload_url):
    """
    Generates contact sheet and screenshots, uploads to Hamster,
    and returns a list of BBCode image links.
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

    # Upload contact sheet and individual screens
    contact_url = upload_file_to_hamster(contact_sheet_path, hamster_api_key, hamster_upload_url)
    screen_urls = [upload_file_to_hamster(f, hamster_api_key, hamster_upload_url) for f in screen_files]

    # Build BBCode
    bbcode_lines = []
    if studio_image_data.get("url"):
        bbcode_lines.append(f"[img]{studio_image_data['url']}[/img]")
    for perf in performer_images_data:
        if perf.get("url"):
            bbcode_lines.append(f"[img]{perf['url']}[/img]")
    if contact_url:
        bbcode_lines.append(f"[img]{contact_url}[/img]")
    for url in screen_urls:
        if url:
            bbcode_lines.append(f"[img]{url}[/img]")

    messagebox.showinfo("Success", "Images generated and uploaded successfully!")
    return bbcode_lines
