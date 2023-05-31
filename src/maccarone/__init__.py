from logging import getLogger

logger = getLogger(__name__)

try:
    import stale_maccarone.enable

    stale_maccarone.enable.enable_py_string_matching = False
    stale_maccarone.enable.fullname_pattern = r"maccarone\..*"
except ImportError:
    logger.debug("no stale_maccarone; assuming source is already preprocessed")

from maccarone.loader import enable
