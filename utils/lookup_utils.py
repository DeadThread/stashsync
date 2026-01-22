# utils/lookup_utils.py

import re
import tkinter as tk
from tkinter import messagebox, ttk
import requests
from utils.image_utils import download_stash_image, build_image_url, display_image
from config import STASH_BASE_URL, STASH_GRAPHQL_URL, DEFAULT_TITLE_FORMAT

# --------------------
# Helpers
# --------------------
def clean_tag(tag_name: str) -> str:
    """Format a tag: lowercase, spaces → periods, remove invalid chars."""
    tag = tag_name.lower()
    tag = tag.replace(" ", ".")
    tag = re.sub(r"[^a-z0-9.]", "", tag)
    tag = re.sub(r"\.+", ".", tag)
    return tag.strip(".")


def format_scene_name(template: str, scene_data: dict) -> str:
    """Generate formatted scene name from template and scene data."""
    if not template or not scene_data:
        return ""

    name = template

    # Simple replacements
    replacements = {
        "[DATE]": scene_data.get("date", ""),
        "[STUDIO]": scene_data.get("studio", {}).get("name", ""),
        "[PARENT_STUDIO]": scene_data.get("studio", {}).get("parentStudio", {}).get("name", ""),
        "[TITLE]": scene_data.get("title", ""),
        "[CONTAINER]": scene_data.get("container", ""),
        "[SIZE]": scene_data.get("size", ""),
        "[FORMAT]": scene_data.get("format", ""),
        "[PERFORMERS]": ", ".join([p.get("name", "") for p in scene_data.get("performers", [])]),
    }

    # Individual performers
    performers = scene_data.get("performers", [])
    for idx, perf in enumerate(performers, start=1):
        replacements[f"[PERFORMER_{idx}]"] = perf.get("name", "")

    # Replace all tokens
    for token, val in replacements.items():
        name = name.replace(token, val)

    # Cleanup double spaces and brackets
    name = re.sub(r"\s+", " ", name).strip()
    name = re.sub(r"\[\[([^\]]+)\]\]", r"[\1]", name)  # normalize [[TOKEN]] → [TOKEN]
    return name


# --------------------
# Lookup Function
# --------------------
def lookup(
    stash_id_entry,
    studio_var,
    title_var,
    desc_text,
    tags_text,
    generate_btn,
    studio_image_label,
    cover_image_label,
    performer_scrollable,
    studio_image_data,
    cover_image_data,
    performer_images_data,
    current_scene_data,
    formatted_title_var=None,
    stash_session=None,
    QUERY=None,
    STASH_GRAPHQL_URL_OVERRIDE=None
):
    """
    Lookup scene by Stash ID and populate GUI:
    - Studio image
    - Cover image
    - Performer images
    - Title, description, tags
    - Formatted title (auto from template)
    """
    STASH_GRAPHQL_URL = STASH_GRAPHQL_URL_OVERRIDE or STASH_GRAPHQL_URL
    stash_session = stash_session or requests.Session()
    QUERY = QUERY or """
        query FindScene($id: ID!) {
            findScene(id: $id) {
                id
                title
                details
                date
                container
                size
                format
                screenshot
                image_path
                cover_image
                paths { screenshot }
                studio { name parentStudio { name } image_path }
                performers { name image_path }
                tags { name }
                files { path duration width height frame_rate bit_rate video_codec audio_codec }
            }
        }
    """

    stash_id = stash_id_entry.get().strip()
    if not stash_id.isdigit():
        print(f"[lookup] Invalid Stash ID: {stash_id}")
        return

    payload = {"query": QUERY, "variables": {"id": stash_id}}

    try:
        print(f"[lookup] Sending request for Stash ID: {stash_id}")
        r = stash_session.post(STASH_GRAPHQL_URL, json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()

        if "errors" in data:
            messagebox.showerror("GraphQL Error", data["errors"][0]["message"])
            print("[lookup] GraphQL returned errors:", data["errors"])
            return

        scene = data.get("data", {}).get("findScene")
        if not scene:
            messagebox.showinfo("Not found", f"Scene {stash_id} not found")
            print(f"[lookup] Scene {stash_id} not found")
            return

        print(f"[lookup] Scene found: {scene.get('title', 'Unknown title')}")

        # Update scene storage
        current_scene_data.clear()
        current_scene_data.update(scene)

        # --------------------
        # Text fields
        # --------------------
        studio_var.set(scene.get("studio", {}).get("name", ""))
        title_var.set(scene.get("title", ""))
        desc_text.delete("1.0", tk.END)
        desc_text.insert(tk.END, scene.get("details") or "")

        # Tags
        tags_formatted = " ".join(clean_tag(t.get("name","")) for t in scene.get("tags", []))
        tags_text.delete("1.0", tk.END)
        tags_text.insert(tk.END, tags_formatted)
        print(f"[lookup] Tags: {tags_formatted}")

        # Generate button
        generate_btn.configure(state="normal" if scene.get("files") else "disabled")

        # --------------------
        # Formatted Title
        # --------------------
        if formatted_title_var:
            formatted_name = format_scene_name(DEFAULT_TITLE_FORMAT, current_scene_data)
            formatted_title_var.set(formatted_name)
            print(f"[lookup] Formatted Title: {formatted_name}")

        # --------------------
        # Studio Image
        # --------------------
        studio_image_data.clear()
        studio = scene.get("studio")
        if studio and studio.get("image_path"):
            url = build_image_url(studio["image_path"])
            img_data = download_stash_image(url, stash_session)
            if img_data:
                studio_image_data.update({"url": url, "data": img_data})
                display_image(img_data, studio_image_label)
                print(f"[lookup] Studio image loaded: {url}")
            else:
                studio_image_label.configure(image="", text="Download failed")
                print(f"[lookup] Studio image download failed: {url}")
        else:
            studio_image_label.configure(image="", text="No image")
            print("[lookup] No studio image found")

        # --------------------
        # Cover Image
        # --------------------
        cover_image_data.clear()
        screenshot_path = (
            scene.get("paths", {}).get("screenshot")
            or scene.get("screenshot")
            or scene.get("image_path")
            or scene.get("cover_image")
            or f"{STASH_BASE_URL}/scene/{stash_id}/screenshot"
        )

        if screenshot_path:
            img_data = download_stash_image(screenshot_path, stash_session)
            if img_data:
                cover_image_data.update({"url": screenshot_path, "data": img_data})
                display_image(img_data, cover_image_label)
                print(f"[lookup] Cover image loaded: {screenshot_path}")
            else:
                cover_image_label.configure(image="", text="Download failed")
                print(f"[lookup] Cover image download failed: {screenshot_path}")
        else:
            cover_image_label.configure(image="", text="No image")
            print("[lookup] No cover image found in scene data")

        # --------------------
        # Performer Images
        # --------------------
        for widget in performer_scrollable.winfo_children():
            widget.destroy()
        performer_images_data.clear()

        row, col, COLUMNS = 0, 0, 2
        for performer in scene.get("performers", []):
            frame = ttk.Frame(performer_scrollable, relief="solid", borderwidth=1)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            ttk.Label(frame, text=performer.get("name", "Unknown"), font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=5)

            if performer.get("image_path"):
                img_label = ttk.Label(frame, relief="solid")
                img_label.pack(fill="both", expand=True, padx=5, pady=5)
                url = build_image_url(performer["image_path"])
                img_data = download_stash_image(url, stash_session)
                if img_data and display_image(img_data, img_label, max_width=130, max_height=180):
                    performer_images_data.append({"name": performer["name"], "url": url, "data": img_data})
                    print(f"[lookup] Performer image loaded: {performer['name']} -> {url}")
                else:
                    img_label.configure(text="Download failed")
                    print(f"[lookup] Performer image download failed: {performer['name']} -> {url}")
            else:
                ttk.Label(frame, text="No image available", relief="solid").pack(fill="both", expand=True, padx=5, pady=5)
                print(f"[lookup] Performer has no image: {performer.get('name')}")

            col += 1
            if col >= COLUMNS:
                col = 0
                row += 1

        for c in range(COLUMNS):
            performer_scrollable.columnconfigure(c, weight=1)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Request failed: {str(e)}")
        print("[lookup] RequestException:", e)
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")
        print("[lookup] Exception:", e)


# --------------------
# Helper: trigger on Stash ID change
# --------------------
def on_id_changed(event, stash_id_entry, lookup_func):
    """Called on KeyRelease to trigger lookup"""
    stash_id = stash_id_entry.get().strip()
    if len(stash_id) >= 4 and stash_id.isdigit():
        print(f"[on_id_changed] Triggering lookup for ID: {stash_id}")
        lookup_func()
