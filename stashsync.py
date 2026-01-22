# stashsync.py
import requests
from config import STASH_GRAPHQL_URL, STASH_API_KEY, HAMSTER_API_KEY, HAMSTER_UPLOAD_URL
from paths.path_mapper import save_path_mappings
from gui.main_gui import create_main_gui
# --------------------
# Stash HTTP Session
# --------------------
stash_session = requests.Session()
stash_session.headers.update({"ApiKey": STASH_API_KEY, "Content-Type": "application/json"})
# --------------------
# Launch GUI
# --------------------
root = create_main_gui(
    stash_session=stash_session,
    QUERY="""
    query FindScene($id: ID!) {
      findScene(id: $id) {
        id
        title
        details
        date
        studio { 
          name 
          image_path 
        }
        performers { 
          name 
          image_path 
        }
        tags { 
          name 
        }
        files { 
          path 
          duration 
          width 
          height 
        }
      }
    }
    """,
    STASH_GRAPHQL_URL=STASH_GRAPHQL_URL,
    HAMSTER_API_KEY=HAMSTER_API_KEY,
    HAMSTER_UPLOAD_URL=HAMSTER_UPLOAD_URL,
    save_path_mappings=save_path_mappings
)
root.mainloop()