import json
import hashlib

def dict_to_hash(d: dict) -> str:
    hasher = hashlib.sha256()

    hasher.update(json.dumps(d).encode("utf-8"))

    return hasher.hexdigest()

class CacheKeyMissingError(Exception):
    pass

class DiskCache:
    """Store and retrieve keys from JSON object on disk."""

    def __init__(self, path):
        self.path = path

    def _read_cache(self) -> dict:
        #<<load from self.path; empty dict on error>>

    def _write_cache(self, cache: dict) -> None:
        #<<write to self.path; human-readable JSON>>

    def get(self, key: str, inputs: dict) -> object:
        cache = self._read_cache()

        try:
            entry = cache[key]

            if entry.get("inputs_hash") != dict_to_hash(inputs):
                raise CacheKeyMissingError()

            return entry["value"]
        except KeyError:
            raise CacheKeyMissingError()

    def set(self, key: str, inputs: dict, value: object) -> None:
        cache = self._read_cache()

        cache[key] = dict(
            inputs_hash=dict_to_hash(inputs),
            value=value,
        )

        self._write_cache(cache)
