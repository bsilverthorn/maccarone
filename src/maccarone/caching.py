import os
import json
import hashlib

def key_to_hash(key: dict) -> str:
    hasher = hashlib.sha256()

    hasher.update(json.dumps(key).encode("utf-8"))

    return hasher.hexdigest()

class CacheKeyMissingError(Exception):
    pass

class DiskCache:
    def __init__(self, cache_dir):
        os.makedirs(cache_dir, exist_ok=True)

        self.cache_dir = cache_dir

    def path(self, key: dict) -> str:
        return os.path.join(
            self.cache_dir,
            key_to_hash(key) + ".json",
        )

    def set(self, key: dict, value: object) -> None:
        with open(self.path(key), "w") as file:
            json.dump(value, file)

    def get(self, key: dict) -> object:
        try:
            with open(self.path(key), "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise CacheKeyMissingError()

default = DiskCache(
    cache_dir=os.environ.get(
        "MACCARONE_CACHE_DIR",
        os.path.expanduser("~/.cache/maccarone"),
    ),
)
