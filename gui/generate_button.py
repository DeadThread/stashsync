# gui/generate_button.py

import tkinter as tk
from tkinter import messagebox
import requests
from utils.upload_utils import generate_and_upload
from config import HAMSTER_API_KEY, HAMSTER_UPLOAD_URL, STASH_BASE_URL

def wire_generate_button(
    generate_btn,
    stash_id_entry,
    studio_var,
    title_var,
    desc_text,
    tags_text,
    studio_image_data,
    performer_images_data,
    current_scene_data,
    bbcode_text,
):
    """
    Wires the 'Generate & Upload Images' button and handles BBCode generation.
    """

    def on_generate_click():
        nonlocal current_scene_data

        # --- Validate scene ID ---
        scene_id = stash_id_entry.get().strip()
        if not scene_id:
            messagebox.showerror("Error", "Scene ID is required for poster upload")
            return
        current_scene_data['scene_id'] = scene_id

        # --- Create Stash session ---
        stash_session = requests.Session()

        # --- Generate and upload images ---
        generate_and_upload(
            current_scene_data=current_scene_data,
            studio_image_data=studio_image_data,
            performer_images_data=performer_images_data,
            title_var=title_var,
            hamster_api_key=HAMSTER_API_KEY,
            hamster_upload_url=HAMSTER_UPLOAD_URL,
            stash_session=stash_session,
            stash_url=STASH_BASE_URL
        )

        # --- Build BBCode ---
        bbcode_lines = []

        # Outer table
        bbcode_lines.append("[bg=#202b33][color=#F5F8FA][font=Helvetica][table=nopad,nball,vat][tr][td=#202b33][/td]")
        bbcode_lines.append("[td=400px,#202b33][bg=90%][size=2]")

        # Studio logo
        studio_url = studio_image_data.get('url', '') if isinstance(studio_image_data, dict) else ''
        if studio_url:
            bbcode_lines.append(f"[center][img=100]{studio_url}[/img][/center]")

        # Title & date
        title = title_var.get() or current_scene_data.get('title', '')
        date = current_scene_data.get('date', '')
        bbcode_lines.append(f"[size=4][font=Arial Black]{title}[/font][/size]")
        bbcode_lines.append(f"[imgnm]https://hamsterimg.net/images/2025/06/21/pad.png[/imgnm]{date}")

        # Details section
        details = current_scene_data.get('details', '')
        bbcode_lines.append("[b]Details[/b]")
        bbcode_lines.append(f"[imgnm]https://hamsterimg.net/images/2025/06/21/pad.png[/imgnm]{details}")

        # Tags
        tags = current_scene_data.get('tags', [])
        if tags:
            tag_names = [t.get('name', '') for t in tags if isinstance(t, dict)]
            if tag_names:
                bbcode_lines.append("[b]Includes[/b]")
                bbcode_lines.append(f"[imgnm]https://hamsterimg.net/images/2025/06/21/pad.png[/imgnm]{', '.join(tag_names)}")

        # Performers
        bbcode_lines.append("[b]Performers[/b][br]")
        bbcode_lines.append("[table=nball,left][tr]")

        performers = current_scene_data.get('performers', [])
        for i, performer in enumerate(performers):
            perf_name = performer.get('name') if isinstance(performer, dict) else str(performer)
            perf_img = ''
            if isinstance(performer_images_data, list) and i < len(performer_images_data):
                p = performer_images_data[i]
                perf_img = p.get('url', '') if isinstance(p, dict) else str(p)
            elif isinstance(performer_images_data, dict):
                perf_img = performer_images_data.get(perf_name, {}).get('url', '') if isinstance(performer_images_data.get(perf_name), dict) else performer_images_data.get(perf_name, '')

            perf_tag = perf_name.lower().replace(' ', '.')
            bbcode_lines.append(f"[td=#30404d,124px][img=123]{perf_img}[/img][url=/torrents.php?taglist={perf_tag}][size=3][/size][color=white][bg=90%]{perf_name}[br][/bg][/color][/url][/td]")
            if i < len(performers) - 1:
                bbcode_lines.append("[td=8px][/td]")

        bbcode_lines.append("[td][/td][/tr][/table]")
        bbcode_lines.append("[/size][/bg][/td]")

        # Right column: poster + video info + screens
        bbcode_lines.append("[td=vat,800px][bg=98%]")
        poster_url = current_scene_data.get('poster_url', '')
        if poster_url:
            bbcode_lines.append(f"[imgnm]{poster_url}[/imgnm]")

        video_file = current_scene_data.get('files', [{}])[0]
        duration_seconds = video_file.get('duration', 0)
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        duration = f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes}:{seconds:02d}"

        width = video_file.get('width', 3840)
        height = video_file.get('height', 2160)
        resolution = f"{width}×{height}"
        fps = f"{video_file.get('frame_rate', 29.97):.2f} fps"
        bit_rate = video_file.get('bit_rate', 0)
        bitrate = f"{bit_rate / 1_000_000:.2f} Mb/s" if bit_rate else "18.22 Mb/s"
        codec = f"{video_file.get('video_codec','h264')}/{video_file.get('audio_codec','aac')}"

        bbcode_lines.append("[bg=#30404d][color=#F0EEEB][size=2]")
        bbcode_lines.append("[table=100%,nball,vam][tr]")
        bbcode_lines.append("[td=16px][/td]")
        bbcode_lines.append(f"[td]{duration}[/td]")
        bbcode_lines.append(f"[td][align=right]mp4   {codec}   {resolution}   {bitrate}   {fps}[/align][/td]")
        bbcode_lines.append("[td=16px][/td]")
        bbcode_lines.append("[/tr][/table][/size][/color][/bg]")
        bbcode_lines.append("[size=2]")

        # Screenshots
        bbcode_lines.append("[b]Screens[/b]")
        screenshot_urls = current_scene_data.get('screenshot_urls', [])
        if screenshot_urls:
            # Just append all images on the same line, separated by nothing
            screen_line = "".join(f"[img=200]{url}[/img]" for url in screenshot_urls)
            bbcode_lines.append(screen_line)

        # Contact sheet
        contact_sheet_url = current_scene_data.get('contact_sheet_url', '')
        if contact_sheet_url:
            bbcode_lines.append("[b]Contact Sheet[/b]")
            bbcode_lines.append("[spoiler=Click to view]")
            bbcode_lines.append(f"[img]{contact_sheet_url}[/img]")
            bbcode_lines.append("[/spoiler]")

        bbcode_lines.append("[/size]")
        bbcode_lines.append("[img]https://hamsterimg.net/images/2025/09/29/space.png[/img]")
        bbcode_lines.append("[/bg][/td][td=#202b33][/td][/tr][/table][/font][/color][/bg]")

        # Insert into BBCode text widget
        bbcode_text.delete("1.0", tk.END)
        bbcode_text.insert(tk.END, "\n".join(bbcode_lines))

    generate_btn.config(command=on_generate_click)
