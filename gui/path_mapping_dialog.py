# gui/path_mapping_dialog.py

# --------------------
# Imports
# --------------------
from tkinter import Toplevel, ttk, messagebox
from paths.path_mapper import load_path_mappings, save_path_mappings

# --------------------
# Path Mapping Dialog
# --------------------
def open_path_mapping_dialog(root):
    """
    Opens a modal dialog to configure Linux -> Windows path mappings
    for Stash video files.
    """
    dialog = Toplevel(root)
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
