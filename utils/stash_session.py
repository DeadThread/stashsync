import requests
from config import STASH_API_KEY

def create_stash_session():
    session = requests.Session()
    session.headers.update({"ApiKey": STASH_API_KEY, "Content-Type": "application/json"})
    return session
