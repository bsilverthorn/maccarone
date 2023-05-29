try:
    import stale_maccarone.enable

    stale_maccarone.enable.enable_py_string_matching = False
    stale_maccarone.enable.fullname_pattern = r"maccarone\..*"
except ImportError:
    pass
