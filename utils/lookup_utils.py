# utils/lookup_utils.py

import re
import tkinter as tk
from tkinter import messagebox
from utils.image_utils import download_stash_image, build_image_url, display_image
import requests
from config import STASH_BASE_URL

def clean_tag(tag_name: str) -> str:
    """Format a tag: lowercase, spaces → periods, remove invalid chars."""
    tag = tag_name.lower()
    tag = tag.replace(" ", ".")
    tag = re.sub(r"[^a-z0-9.]", "", tag)
    tag = re.sub(r"\.+", ".", tag)
    return tag.strip(".")


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
    stash_session,
    QUERY,
    STASH_GRAPHQL_URL
):
    """Lookup scene by Stash ID and populate GUI with studio, cover, and performer images."""
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

        # Update global storage
        current_scene_data.clear()
        current_scene_data.update(scene)

        # --------------------
        # Update text fields
        # --------------------
        studio_var.set(scene.get("studio", {}).get("name") or "")
        title_var.set(scene.get("title") or "")
        desc_text.delete("1.0", tk.END)
        desc_text.insert(tk.END, scene.get("details") or "")

        # Tags
        tags_formatted = " ".join(clean_tag(t["name"]) for t in scene.get("tags", []))
        tags_text.delete("1.0", tk.END)
        tags_text.insert(tk.END, tags_formatted)
        print(f"[lookup] Tags: {tags_formatted}")

        # Enable generate button if files exist
        generate_btn.configure(state="normal" if scene.get("files") else "disabled")

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
        screenshot_path = None

        # Try all sources like generate logic
        if scene.get("paths", {}).get("screenshot"):
            screenshot_path = scene["paths"]["screenshot"]
            print(f"[lookup] Found cover in paths.screenshot: {screenshot_path}")
        elif scene.get("screenshot"):
            screenshot_path = scene["screenshot"]
            print(f"[lookup] Found cover in screenshot key: {screenshot_path}")
        elif scene.get("image_path"):
            screenshot_path = scene["image_path"]
            print(f"[lookup] Found cover in image_path: {screenshot_path}")
        elif scene.get("cover_image"):
            screenshot_path = scene["cover_image"]
            print(f"[lookup] Found cover in cover_image: {screenshot_path}")
        elif stash_id_entry.get().strip():
            scene_id = stash_id_entry.get().strip()
            screenshot_path = f"{STASH_BASE_URL}/scene/{scene_id}/screenshot"
            print(f"[lookup] Using fallback cover URL from Stash ID: {screenshot_path}")

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
            frame = tk.ttk.Frame(performer_scrollable, relief="solid", borderwidth=1)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            tk.ttk.Label(frame, text=performer.get("name", "Unknown"), font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=5)

            if performer.get("image_path"):
                img_label = tk.ttk.Label(frame, relief="solid")
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
                tk.ttk.Label(frame, text="No image available", relief="solid").pack(fill="both", expand=True, padx=5, pady=5)
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


def on_id_changed(event, stash_id_entry, lookup_func):
    """Called on KeyRelease to trigger lookup"""
    stash_id = stash_id_entry.get().strip()
    if len(stash_id) >= 4 and stash_id.isdigit():
        print(f"[on_id_changed] Triggering lookup for ID: {stash_id}")
        lookup_func()
