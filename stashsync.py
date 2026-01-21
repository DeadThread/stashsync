import tkinter as tk

from config import (
    STASH_GRAPHQL_URL,
    HAMSTER_UPLOAD_URL,
    HAMSTER_API_KEY,
)
from gui.path_mapping_dialog import open_path_mapping_dialog
from gui.gui_main import build_main_gui
from gui.event_bindings import bind_stash_events
from graphql.queries import FIND_SCENE_QUERY as QUERY
from utils.stash_session import create_stash_session
# Initialize
stash_session = create_stash_session()
# Build GUI
root, widgets = build_main_gui(open_path_mapping_dialog)
# Storage
studio_image_data = {}
performer_images_data = []
current_scene_data = {}
# Bind events
bind_stash_events(
    widgets,
    studio_image_data,
    performer_images_data,
    current_scene_data,
    stash_session,
    QUERY,
)
# Run GUI
root.mainloop()