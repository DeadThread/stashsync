# stashsync.py

# --------------------
# Imports
# --------------------
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import io
import os
import tempfile
from PIL import Image, ImageTk

from config import (
    STASH_GRAPHQL_URL,
    STASH_API_KEY,
    HAMSTER_UPLOAD_URL,
    HAMSTER_API_KEY,
    CONFIG_FILE,
    CONTACT_ROWS,
    CONTACT_COLS,
    THUMB_WIDTH,
    THUMB_HEIGHT,
    CONTACT_HEADER_HEIGHT,
)

# Path mapping utilities
from paths.path_mapper import load_path_mappings, save_path_mappings, map_path

# Image utilities
from utils.image_utils import download_stash_image, build_image_url, format_duration

# Upload / generate utilities
from utils.upload_utils import generate_and_upload

# Lookup / ID change utilities
from utils.lookup_utils import lookup, on_id_changed

# FFmpeg utilities
from utils.ffmpeg_utils import generate_contact_sheet, generate_individual_screens

# --------------------
# GraphQL Query
# --------------------
QUERY = """
query FindScene($id: ID!) {
  findScene(id: $id) {
    title
    details
    studio {
      name
      image_path
    }
    performers {
      name
      image_path
    }
    tags { name }
    files {
      path
      duration
      width
      height
    }
  }
}
"""

# --------------------
# Stash HTTP Session
# --------------------
stash_session = requests.Session()
stash_session.headers.update({"ApiKey": STASH_API_KEY, "Content-Type": "application/json"})

# --------------------
# Path Mapping Dialog
# --------------------
def open_path_mapping_dialog(root):
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
# GUI Setup
# --------------------
root = tk.Tk()
root.title("Stash Lookup")
root.geometry("1100x750")
root.resizable(False, False)

menubar = tk.Menu(root)
root.config(menu=menubar)
settings_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Path Mappings", command=lambda: open_path_mapping_dialog(root))

container = ttk.Frame(root)
container.pack(fill="both", expand=True, padx=10, pady=10)

left_panel = ttk.Frame(container)
left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
right_panel = ttk.Frame(container)
right_panel.grid(row=0, column=1, sticky="nsew")
container.columnconfigure(0, weight=1)
container.columnconfigure(1, weight=0)

# --------------------
# ID Entry
# --------------------
id_frame = ttk.Frame(left_panel)
id_frame.pack(fill="x", pady=(0, 10))
ttk.Label(id_frame, text="Stash ID").pack(side="left", padx=(0, 10))
stash_id_entry = ttk.Entry(id_frame, width=20)
stash_id_entry.pack(side="left")

# Studio, Title, Description, Tags
studio_var = tk.StringVar()
title_var = tk.StringVar()
studio_entry = ttk.Entry(left_panel, textvariable=studio_var, width=60)
studio_entry.pack(fill="x", pady=(0, 10))
title_entry = ttk.Entry(left_panel, textvariable=title_var, width=60)
title_entry.pack(fill="x", pady=(0, 10))
desc_text = tk.Text(left_panel, height=8, wrap="word")
desc_text.pack(fill="x", pady=(0, 10))
tags_text = tk.Text(left_panel, height=4, wrap="word")
tags_text.pack(fill="x", pady=(0, 10))

generate_btn = ttk.Button(left_panel, text="Generate & Upload Images", state="disabled")
generate_btn.pack(fill="x", pady=(5, 5))
bbcode_text = scrolledtext.ScrolledText(left_panel, height=8, wrap="word")
bbcode_text.pack(fill="both", expand=True)

# Right Panel
studio_images_frame = ttk.LabelFrame(right_panel, text="Studio Images", padding=10)
studio_images_frame.pack(fill="x", pady=(0, 10))
studio_image_label = ttk.Label(studio_images_frame, text="No image", relief="solid")
studio_image_label.pack(fill="both", expand=True, padx=5, pady=5)

performer_images_frame = ttk.LabelFrame(right_panel, text="Performer Images", padding=10)
performer_images_frame.pack(fill="both", expand=True)
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

# Storage
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
            studio_image_label,
            performer_scrollable,
            studio_image_data,
            performer_images_data,
            current_scene_data,
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
    global current_scene_data
    bbcode_lines = generate_and_upload(
        current_scene_data=current_scene_data,
        studio_image_data=studio_image_data,
        performer_images_data=performer_images_data,
        title_var=title_var,
        hamster_api_key=HAMSTER_API_KEY,
        hamster_upload_url=HAMSTER_UPLOAD_URL,
    )
    if bbcode_lines:  # only insert if we got something
        bbcode_text.delete("1.0", tk.END)
        bbcode_text.insert(tk.END, "\n".join(bbcode_lines))

generate_btn.config(command=on_generate_click)

# --------------------
# Run GUI
# --------------------
root.mainloop()
