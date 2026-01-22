import re
import tkinter as tk
from tkinter import ttk, messagebox
from utils.image_utils import download_stash_image, build_image_url, display_image
from paths.path_mapper import load_path_mappings, map_path
import requests



def lookup(
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
):
    """Lookup scene by Stash ID and populate GUI"""
    global_vars = {
        "studio_image_data": studio_image_data,
        "performer_images_data": performer_images_data,
        "current_scene_data": current_scene_data
    }

    stash_id = stash_id_entry.get().strip()
    if not stash_id.isdigit():
        return

    payload = {"query": QUERY, "variables": {"id": stash_id}}
    try:
        r = stash_session.post(STASH_GRAPHQL_URL, json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "errors" in data:
            messagebox.showerror("GraphQL Error", data["errors"][0]["message"])
            return

        scene = data.get("data", {}).get("findScene")
        if not scene:
            messagebox.showinfo("Not found", "Scene not found")
            return

        # Update global storage
        global_vars["current_scene_data"].clear()
        global_vars["current_scene_data"].update(scene)

        # GUI updates
        studio_var.set(scene.get("studio", {}).get("name") or "")
        title_var.set(scene.get("title") or "")
        desc_text.delete("1.0", tk.END)
        desc_text.insert(tk.END, scene.get("details") or "")

        # Format tags: lowercase, spaces → periods, remove special characters, separated by spaces
        def clean_tag(tag_name):
            # Lowercase
            tag = tag_name.lower()
            # Replace spaces with periods
            tag = tag.replace(" ", ".")
            # Remove all characters except letters, numbers, and periods
            tag = re.sub(r"[^a-z0-9.]", "", tag)
            # Collapse multiple periods into one
            tag = re.sub(r"\.+", ".", tag)
            # Strip leading/trailing periods
            tag = tag.strip(".")
            return tag

        tags_formatted = " ".join(clean_tag(t["name"]) for t in scene.get("tags", []))

        tags_text.delete("1.0", tk.END)
        tags_text.insert(tk.END, tags_formatted)


        generate_btn.configure(state="normal" if scene.get("files") else "disabled")

        # Studio Image
        studio_image_data.clear()
        studio = scene.get("studio")
        if studio and studio.get("image_path"):
            url = build_image_url(studio['image_path'])
            img_data = download_stash_image(url, stash_session)
            if img_data:
                studio_image_data.update({'url': url, 'data': img_data})
                display_image(img_data, studio_image_label)
            else:
                studio_image_label.configure(image="", text="Download failed")
        else:
            studio_image_label.configure(image="", text="No image")

        # Performer Images
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
                url = build_image_url(performer['image_path'])
                img_data = download_stash_image(url, stash_session)
                if img_data and display_image(img_data, img_label, max_width=130, max_height=180):
                    performer_images_data.append({'name': performer["name"], 'url': url, 'data': img_data})
                else:
                    img_label.configure(text="Download failed")
            else:
                ttk.Label(frame, text="No image available", relief="solid").pack(fill="both", expand=True, padx=5, pady=5)

            col += 1
            if col >= COLUMNS:
                col = 0
                row += 1

        for c in range(COLUMNS):
            performer_scrollable.columnconfigure(c, weight=1)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Request failed: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")


def on_id_changed(event, stash_id_entry, lookup_func):
    """Called on KeyRelease to trigger lookup"""
    stash_id = stash_id_entry.get().strip()
    if len(stash_id) >= 4 and stash_id.isdigit():
        lookup_func()

