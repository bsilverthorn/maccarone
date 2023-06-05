import os.path

from tempfile import TemporaryDirectory

from maccarone.caching import (
    DiskCache,
    CacheKeyMissingError,
)

def test_disk_cache_set_get():
    with TemporaryDirectory() as cache_dir:
        cache = DiskCache(os.path.join(cache_dir, "cache.json"))

        name = "foo"
        inputs = {"a": 1, "b": 2}
        value = {"c": 3, "d": 4}

        try:
            cache.get(name, inputs)
        except CacheKeyMissingError:
            pass
        else:
            assert False, "expected CacheKeyMissingError"

        cache.set(name, inputs, value)

        assert cache.get(name, inputs) == value
