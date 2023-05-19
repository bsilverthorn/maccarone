import os
import json
import hashlib

def key_to_hash(key: dict) -> str:
    hasher = hashlib.sha256()

    hasher.update(json.dumps(key))

    return hasher.hexdigest()

class DiskCache:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir

    def path(self, key: dict) -> str:
        return os.path.join(
            self.cache_dir,
            key_to_hash(key),
        )

    def try_get(self, key: dict) -> object:
        try:
            with open(self.path(key), "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return None

default = DiskCache(
    cache_dir=os.environ.get(
        "MACCARONE_CACHE_DIR",
        os.path.expanduser("~/.cache/maccarone"),
    ),
)
