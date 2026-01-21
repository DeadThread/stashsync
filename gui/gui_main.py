import tkinter as tk
from tkinter import ttk, scrolledtext

def build_main_gui(open_path_mapping_dialog):
    """
    Build and return the main GUI for Stash Lookup.
    Returns:
        root: The Tk root window
        widgets: dict of key widgets for later use
    """
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

    # Return root and key widgets for later use
    widgets = {
        "stash_id_entry": stash_id_entry,
        "studio_var": studio_var,
        "title_var": title_var,
        "studio_entry": studio_entry,
        "title_entry": title_entry,
        "desc_text": desc_text,
        "tags_text": tags_text,
        "generate_btn": generate_btn,
        "bbcode_text": bbcode_text,
        "studio_image_label": studio_image_label,
        "performer_scrollable": performer_scrollable,
        "performer_canvas": performer_canvas,
    }

    return root, widgets
