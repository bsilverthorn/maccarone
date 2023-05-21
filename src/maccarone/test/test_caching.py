from tempfile import TemporaryDirectory

from maccarone.caching import (
    DiskCache,
    CacheKeyMissingError,
)

def test_disk_cache_set_get():
    with TemporaryDirectory() as cache_dir:
        cache = DiskCache(cache_dir)

        key = {"a": 1, "b": 2}
        value = {"c": 3, "d": 4}

        try:
            cache.get(key)
        except CacheKeyMissingError:
            pass
        else:
            assert False, "expected CacheKeyMissingError"

        cache.set(key, value)

        assert cache.get(key) == value
