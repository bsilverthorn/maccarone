from tempfile import TemporaryDirectory

from maccarone.caching import DiskCache

def test_disk_cache_set_get():
    with TemporaryDirectory() as cache_dir:
        cache = DiskCache(cache_dir)

        key = {"a": 1, "b": 2}
        value = {"c": 3, "d": 4}

        assert cache.get(key) is None

        cache.set(key, value)

        assert cache.get(key) == value
