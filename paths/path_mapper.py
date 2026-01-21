# paths/path_mapper.py

import os
import json
from config import CONFIG_FILE


def load_path_mappings():
    """Load path mappings from config file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        # Default mappings
        return {
            "/data/Extra": "X:\\",
            "/data/Extra-II": "H:\\",
        }

    except Exception as e:
        print(f"[path_mapper] Error loading path mappings: {e}")
        return {}


def save_path_mappings(mappings: dict) -> bool:
    """Save path mappings to config file"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(mappings, f, indent=2)
        return True

    except Exception as e:
        print(f"[path_mapper] Error saving path mappings: {e}")
        return False


def map_path(linux_path: str, mappings: dict) -> str:
    """
    Convert Linux path to Windows path using mappings.
    Longest prefix wins.
    """
    if not linux_path:
        return linux_path

    linux_path = linux_path.replace("\\", "/")

    # Longest prefix first
    for linux_prefix, windows_prefix in sorted(
        mappings.items(),
        key=lambda x: len(x[0]),
        reverse=True,
    ):
        if linux_path.startswith(linux_prefix):
            relative_path = linux_path[len(linux_prefix):].lstrip("/")

            if not windows_prefix.endswith("\\"):
                windows_prefix += "\\"

            return windows_prefix + relative_path.replace("/", "\\")

    print(f"[path_mapper] Warning: No mapping found for path: {linux_path}")
    return linux_path
