"StashSync"

description: "StashSync is a GUI application for looking up scenes from your Stash server, generating contact sheets, and uploading images to HamsterImg."

requirements:
  python: "3.12+"
  libraries:
    - "Tkinter (usually included with Python)"
    - "Requests"
    - "Pillow"
    - "Other dependencies (install with `pip install -r requirements.txt`)"
    
  ffmpeg:
    note: "Place `ffmpeg.exe` (Windows) or `ffmpeg` (Linux/macOS) in the root of the project."
    purpose: "Required for generating contact sheets and video thumbnails."

setup:

  clone_repository:
    - "git clone https://github.com/DeadThread/stashsync.git"
    - "cd stashsync"
    
  install_dependencies:
    - "pip install -r requirements.txt"
    
  configure_secrets:
    steps:
      - "Copy `config_example.py` to `config.py`"
      - "Edit `config.py` and fill in:"
      - "  - STASH_BASE_URL and STASH_API_KEY"
      - "  - HAMSTER_UPLOAD_URL and HAMSTER_API_KEY"

running:

  command: "python stashsync.py"
  
  usage:
    - "Enter a Stash scene ID in the GUI"
    - "Lookup scene details"
    - "Generate and upload images"
    - "BBCode output will appear in the GUI"

notes:

  - "Make sure FFmpeg is present in the root of the app."
  - "All sensitive information is stored in `config.py` (which is ignored by Git)."
  - "Development is done in the `dev` branch; stable releases are in `master`."
