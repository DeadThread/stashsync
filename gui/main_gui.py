# gui/main_gui.py

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from paths.path_mapper import load_path_mappings
from utils.lookup_utils import lookup, on_id_changed
from utils.upload_utils import generate_and_upload
from config import HAMSTER_API_KEY, HAMSTER_UPLOAD_URL, STASH_BASE_URL


# --------------------
# Path Mapping Dialog
# --------------------
def open_path_mapping_dialog(root, save_path_mappings):
    dialog = tk.Toplevel(root)
    dialog.title("Path Mappings")
    dialog.geometry("600x400")
    dialog.transient(root)
    dialog.grab_set()

    ttk.Label(dialog, text="Configure Linux to Windows Path Mappings", font=("Arial", 12, "bold")).pack(pady=10)
    ttk.Label(dialog, text="Map Linux paths (from Stash) to Windows drive letters").pack(pady=5)

    mappings_frame = ttk.Frame(dialog)
    mappings_frame.pack(fill="both", expand=True, padx=20, pady=10)

    header_frame = ttk.Frame(mappings_frame)
    header_frame.pack(fill="x", pady=5)
    ttk.Label(header_frame, text="Linux Path", width=30).pack(side="left", padx=5)
    ttk.Label(header_frame, text="Windows Path", width=30).pack(side="left", padx=5)

    current_mappings = load_path_mappings()
    mapping_entries = []

    for linux_path, windows_path in current_mappings.items():
        entry_frame = ttk.Frame(mappings_frame)
        entry_frame.pack(fill="x", pady=2)
        linux_entry = ttk.Entry(entry_frame, width=35)
        linux_entry.insert(0, linux_path)
        linux_entry.pack(side="left", padx=5)
        windows_entry = ttk.Entry(entry_frame, width=35)
        windows_entry.insert(0, windows_path)
        windows_entry.pack(side="left", padx=5)
        mapping_entries.append((linux_entry, windows_entry))

    def add_mapping_row():
        entry_frame = ttk.Frame(mappings_frame)
        entry_frame.pack(fill="x", pady=2)
        linux_entry = ttk.Entry(entry_frame, width=35)
        linux_entry.pack(side="left", padx=5)
        windows_entry = ttk.Entry(entry_frame, width=35)
        windows_entry.pack(side="left", padx=5)
        mapping_entries.append((linux_entry, windows_entry))

    ttk.Button(dialog, text="Add Mapping", command=add_mapping_row).pack(pady=5)

    def save_and_close():
        new_mappings = {}
        for linux_entry, windows_entry in mapping_entries:
            linux_path = linux_entry.get().strip()
            windows_path = windows_entry.get().strip()
            if linux_path and windows_path:
                new_mappings[linux_path] = windows_path
        if save_path_mappings(new_mappings):
            messagebox.showinfo("Success", "Path mappings saved successfully!")
            dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to save path mappings")

    buttons_frame = ttk.Frame(dialog)
    buttons_frame.pack(pady=10)
    ttk.Button(buttons_frame, text="Save", command=save_and_close).pack(side="left", padx=5)
    ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)


# --------------------
# GUI Creation
# --------------------
def create_main_gui(
    stash_session,
    QUERY,
    STASH_GRAPHQL_URL,
    HAMSTER_API_KEY,
    HAMSTER_UPLOAD_URL,
    save_path_mappings,
):
    """Creates the main GUI and returns widgets needed for interactions"""
    root = tk.Tk()
    root.title("Stash Lookup")
    root.geometry("1100x750")
    root.resizable(False, False)

    # --------------------
    # Menubar
    # --------------------
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Settings menu
    settings_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Settings", menu=settings_menu)

    # Path Mappings (existing)
    settings_menu.add_command(
        label="Path Mappings",
        command=lambda: open_path_mapping_dialog(root, save_path_mappings)
    )


    # --------------------
    # Main container layout
    # --------------------
    container = ttk.Frame(root)
    container.pack(fill="both", expand=True, padx=10, pady=10)

    left_panel = ttk.Frame(container)
    left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    right_panel = ttk.Frame(container)
    right_panel.grid(row=0, column=1, sticky="nsew")

    container.columnconfigure(0, weight=1)
    container.columnconfigure(1, weight=0)



    # --------------------
    # Stash ID Entry
    # --------------------
    id_frame = ttk.Frame(left_panel)
    id_frame.pack(fill="x", pady=(0, 10))
    ttk.Label(id_frame, text="Stash ID").pack(side="left", padx=(0, 10))
    stash_id_entry = ttk.Entry(id_frame, width=20)
    stash_id_entry.pack(side="left")

    # --------------------
    # Studio
    # --------------------
    studio_var = tk.StringVar()
    studio_frame = ttk.Frame(left_panel)
    studio_frame.pack(fill="x", pady=(0, 10))
    ttk.Label(studio_frame, text="Studio").pack(side="left", padx=(0, 10))
    studio_entry = ttk.Entry(studio_frame, textvariable=studio_var, width=50)
    studio_entry.pack(side="left")
    ttk.Button(
        studio_frame,
        text="Copy",
        width=6,
        command=lambda: (
            root.clipboard_clear(),
            root.clipboard_append(studio_var.get())
        )
    ).pack(side="left", padx=5)

    # --------------------
    # Title
    # --------------------
    title_var = tk.StringVar()
    title_frame = ttk.Frame(left_panel)
    title_frame.pack(fill="x", pady=(0, 10))
    ttk.Label(title_frame, text="Title").pack(side="left", padx=(0, 10))
    title_entry = ttk.Entry(title_frame, textvariable=title_var, width=50)
    title_entry.pack(side="left")
    ttk.Button(
        title_frame,
        text="Copy",
        width=6,
        command=lambda: (
            root.clipboard_clear(),
            root.clipboard_append(title_var.get())
        )
    ).pack(side="left", padx=5)

    # --------------------
    # Formatted Title
    # --------------------
    formatted_title_var = tk.StringVar()
    formatted_title_frame = ttk.Frame(left_panel)
    formatted_title_frame.pack(fill="x", pady=(0, 10))  # snug under Title
    ttk.Label(formatted_title_frame, text="Formatted Title").pack(side="left", padx=(0, 10))
    formatted_title_entry = ttk.Entry(formatted_title_frame, textvariable=formatted_title_var, width=50)
    formatted_title_entry.pack(side="left")
    ttk.Button(
        formatted_title_frame,
        text="Copy",
        width=6,
        command=lambda: (
            root.clipboard_clear(),
            root.clipboard_append(formatted_title_var.get())
        )
    ).pack(side="left", padx=5)

    # --------------------
    # Description
    # --------------------
    desc_frame = ttk.Frame(left_panel)
    desc_frame.pack(fill="x", pady=(0, 10))
    ttk.Label(desc_frame, text="Description").grid(row=0, column=0, sticky="w", padx=(0, 10))
    desc_text = tk.Text(desc_frame, height=8, wrap="word")
    desc_text.grid(row=0, column=1, sticky="ew")
    desc_copy_btn = ttk.Button(
        desc_frame,
        text="Copy",
        width=6,
        command=lambda: (
            root.clipboard_clear(),
            root.clipboard_append(desc_text.get("1.0", tk.END).strip())
        )
    )
    desc_copy_btn.grid(row=0, column=2, padx=(5, 0))
    desc_frame.columnconfigure(1, weight=1)


    # --------------------
    # Tags
    # --------------------
    tags_frame = ttk.Frame(left_panel)
    tags_frame.pack(fill="x", pady=(0, 10))
    ttk.Label(tags_frame, text="Tags").grid(row=0, column=0, sticky="w", padx=(0, 10))
    tags_text = tk.Text(tags_frame, height=4, wrap="word")
    tags_text.grid(row=0, column=1, sticky="ew")
    tags_copy_btn = ttk.Button(
        tags_frame,
        text="Copy",
        width=6,
        command=lambda: (
            root.clipboard_clear(),
            root.clipboard_append(tags_text.get("1.0", tk.END).strip())
        )
    )
    tags_copy_btn.grid(row=0, column=2, padx=(5, 0))
    tags_frame.columnconfigure(1, weight=1)

    # Generate button
    generate_btn = ttk.Button(left_panel, text="Generate & Upload Images", state="disabled")
    generate_btn.pack(fill="x", pady=(5, 5))

    # BBCode Text (do NOT expand vertically)
    bbcode_text = scrolledtext.ScrolledText(left_panel, height=8, wrap="word")
    bbcode_text.pack(fill="x", pady=(0,5))  # only fill horizontally, not vertically

    # Copy BBCode Button
    bbcode_copy_btn = ttk.Button(
        left_panel,
        text="Copy BBCode",
        width=12,
        command=lambda: (
            root.clipboard_clear(),
            root.clipboard_append(bbcode_text.get("1.0", tk.END).strip())
        )
    )
    bbcode_copy_btn.pack(pady=(0, 10))


    # --------------------
    # Studio Images
    # --------------------
    studio_images_frame = ttk.LabelFrame(right_panel, text="Studio Images", padding=10)
    studio_images_frame.pack(fill="x", pady=(0, 10))
    studio_image_label = ttk.Label(studio_images_frame, text="No image", relief="solid")
    studio_image_label.pack(fill="both", expand=True, padx=5, pady=5)

    # --------------------
    # Cover Image
    # --------------------
    cover_image_frame = ttk.LabelFrame(right_panel, text="Cover Image", padding=10)
    cover_image_frame.pack(fill="x", pady=(0, 10))  # <--- small gap only

    cover_image_label = ttk.Label(cover_image_frame, text="No image", relief="solid")
    cover_image_label.pack(fill="both", expand=True, padx=5, pady=5)

    cover_image_data = {}  # storage for cover image

    # --------------------
    # Cover Image URL 
    # --------------------
    caption_var = tk.StringVar()
    caption_frame = ttk.Frame(right_panel)
    caption_frame.pack(fill="x", pady=(0, 5))  # snug under cover image

    # Label
    ttk.Label(caption_frame, text="Cover Image URL").pack(side="left", padx=(0, 5))

    # Read-only Entry
    caption_entry = ttk.Entry(caption_frame, textvariable=caption_var, state="readonly")
    caption_entry.pack(side="left", fill="x", expand=True)

    # Copy button
    ttk.Button(
        caption_frame,
        text="Copy",
        width=6,
        command=lambda: (
            root.clipboard_clear(),
            root.clipboard_append(caption_var.get())
        )
    ).pack(side="left", padx=(5, 0))    

    # --------------------
    # Performer Images
    # --------------------
    performer_images_frame = ttk.LabelFrame(right_panel, text="Performer Images", padding=10)
    performer_images_frame.pack(fill="both", expand=True, pady=(0, 0))  # <--- snug under cover

    performer_canvas = tk.Canvas(performer_images_frame, height=300)
    performer_scrollbar = ttk.Scrollbar(performer_images_frame, orient="vertical", command=performer_canvas.yview)
    performer_scrollable = ttk.Frame(performer_canvas)
    performer_scrollable.bind(
        "<Configure>",
        lambda e: performer_canvas.configure(scrollregion=performer_canvas.bbox("all"))
    )
    performer_canvas.create_window((0, 0), window=performer_scrollable, anchor="nw")
    performer_canvas.configure(yscrollcommand=performer_scrollbar.set)
    performer_canvas.pack(side="left", fill="both", expand=True)
    performer_scrollbar.pack(side="right", fill="y")


    # --------------------
    # Storage
    # --------------------
    studio_image_data = {}
    performer_images_data = []
    current_scene_data = {}

    # --------------------
    # Bind the Stash ID Entry
    # --------------------
    stash_id_entry.bind(
        "<KeyRelease>",
        lambda e: on_id_changed(
            e,
            stash_id_entry,
            lambda: lookup(
                stash_id_entry,
                studio_var,
                title_var,
                desc_text,
                tags_text,
                generate_btn,
                studio_image_label,         # existing
                cover_image_label,          # existing
                performer_scrollable,
                studio_image_data,
                cover_image_data,           # existing
                performer_images_data,
                current_scene_data,
                formatted_title_var,        # <--- NEW: passes the Formatted Title StringVar
                stash_session,
                QUERY,
                STASH_GRAPHQL_URL
            )
        )
    )

    # --------------------
    # Wire Generate Button
    # --------------------
    def on_generate_click():
        nonlocal current_scene_data

        # Create a session for Stash API calls
        import requests
        stash_session = requests.Session()

        # --- Read scene ID from entry ---
        scene_id = stash_id_entry.get().strip()
        if not scene_id:
            messagebox.showerror("Error", "Scene ID is required for poster upload")
            return
        current_scene_data['scene_id'] = scene_id

        # --- Generate and upload images ---
        bbcode_lines = generate_and_upload(
            current_scene_data=current_scene_data,
            studio_image_data=studio_image_data,
            performer_images_data=performer_images_data,
            title_var=title_var,
            hamster_api_key=HAMSTER_API_KEY,
            hamster_upload_url=HAMSTER_UPLOAD_URL,
            stash_session=stash_session,
            stash_url=STASH_BASE_URL
        )

        if not bbcode_lines:
            return

        # --- Update Cover Image URL read-only entry ---
        caption_var.set(current_scene_data.get('poster_url', ''))

        # --- Build formatted BBCode for the text widget ---
        bbcode_formatted = []

        # Outer table
        bbcode_formatted.append("[bg=#202b33][color=#F5F8FA][font=Helvetica][table=nopad,nball,vat][tr][td=#202b33][/td]")
        bbcode_formatted.append("[td=400px,#202b33][bg=90%][size=2]")

        # Studio logo
        studio_url = studio_image_data.get('url', '') if isinstance(studio_image_data, dict) else ''
        if studio_url:
            bbcode_formatted.append(f"[center][img=100]{studio_url}[/img][/center]")

        # Title and date
        title = title_var.get() or current_scene_data.get('title', '')
        date = current_scene_data.get('date', '')
        bbcode_formatted.append(f"[size=4][font=Arial Black]{title}[/font][/size]")
        bbcode_formatted.append(f"[imgnm]https://hamsterimg.net/images/2025/06/21/pad.png[/imgnm]{date}")

        # Details
        details = current_scene_data.get('details', '')
        bbcode_formatted.append("[b]Details[/b]")
        bbcode_formatted.append(f"[imgnm]https://hamsterimg.net/images/2025/06/21/pad.png[/imgnm]{details}")

        # Tags / Includes
        tags = current_scene_data.get('tags', [])
        if tags:
            tag_names = [tag.get('name', '') for tag in tags if isinstance(tag, dict)]
            if tag_names:
                bbcode_formatted.append("[b]Includes[/b]")
                bbcode_formatted.append(f"[imgnm]https://hamsterimg.net/images/2025/06/21/pad.png[/imgnm]{', '.join(tag_names)}")

        # Performers
        bbcode_formatted.append("[b]Performers[/b][br]")
        bbcode_formatted.append("[table=nball,left][tr]")

        performers = current_scene_data.get('performers', [])
        for i, performer in enumerate(performers):
            if isinstance(performer, dict):
                perf_name = performer.get('name', str(performer))
            else:
                perf_name = str(performer)

            perf_img = ''
            if isinstance(performer_images_data, list) and i < len(performer_images_data):
                perf_img = performer_images_data[i].get('url', '') if isinstance(performer_images_data[i], dict) else performer_images_data[i]

            perf_tag = perf_name.lower().replace(' ', '.')
            bbcode_formatted.append(
                f"[td=#30404d,124px][img=123]{perf_img}[/img][url=/torrents.php?taglist={perf_tag}]"
                f"[size=3][/size][color=white][bg=90%]{perf_name}[br][/bg][/color][/url][/td]"
            )

            if i < len(performers) - 1:
                bbcode_formatted.append("[td=8px][/td]")

        bbcode_formatted.append("[td][/td][/tr][/table]")
        bbcode_formatted.append("[/size][/bg][/td]")

        # Right column with poster, video info, screens, contact sheet
        bbcode_formatted.append("[td=vat,800px][bg=98%]")

        poster_url = current_scene_data.get('poster_url', '')
        if poster_url:
            bbcode_formatted.append(f"[imgnm]{poster_url}[/imgnm]")

        video_file = current_scene_data.get('files', [{}])[0]
        duration_seconds = video_file.get('duration', 0)
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        duration = f"{hours}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes}:{seconds:02d}"

        width = video_file.get('width', 3840)
        height = video_file.get('height', 2160)
        resolution = f"{width}×{height}"

        frame_rate = video_file.get('frame_rate', 29.97)
        fps = f"{frame_rate:.2f} fps"

        bit_rate = video_file.get('bit_rate', 0)
        bitrate = f"{bit_rate / 1_000_000:.2f} Mb/s" if bit_rate else "18.22 Mb/s"

        codec = f"{video_file.get('video_codec', 'h264')}/{video_file.get('audio_codec', 'aac')}"

        bbcode_formatted.append("[bg=#30404d][color=#F0EEEB][size=2]")
        bbcode_formatted.append("[table=100%,nball,vam][tr][td=16px][/td]")
        bbcode_formatted.append(f"[td]{duration}[/td]")
        bbcode_formatted.append(f"[td][align=right]mp4   {codec}   {resolution}   {bitrate}   {fps}[/align][/td]")
        bbcode_formatted.append("[td=16px][/td][/tr][/table][/size][/color][/bg]")
        bbcode_formatted.append("[size=2]")

        # Screenshots
        bbcode_formatted.append("[b]Screens[/b]")
        screenshot_urls = current_scene_data.get('screenshot_urls', [])
        if screenshot_urls:
            line = "".join([f"[img=200]{url}[/img]" for url in screenshot_urls])
            bbcode_formatted.append(line)

        # Contact sheet
        contact_sheet_url = current_scene_data.get('contact_sheet_url', '')
        if contact_sheet_url:
            bbcode_formatted.append("[b]Contact Sheet[/b]")
            bbcode_formatted.append("[spoiler=Click to view]")
            bbcode_formatted.append(f"[img]{contact_sheet_url}[/img]")
            bbcode_formatted.append("[/spoiler]")

        bbcode_formatted.append("[/size]")
        bbcode_formatted.append("[img]https://hamsterimg.net/images/2025/09/29/space.png[/img]")
        bbcode_formatted.append("[/bg][/td][td=#202b33][/td][/tr][/table][/font][/color][/bg]")

        # Insert BBCode into text widget
        bbcode_text.delete("1.0", tk.END)
        bbcode_text.insert(tk.END, "\n".join(bbcode_formatted))


    # --- Attach the handler to the button ---
    generate_btn.config(command=on_generate_click)


    return root
