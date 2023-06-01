from logging import getLogger

logger = getLogger(__name__)

try:
    import stale_maccarone
except ImportError:
    logger.debug("no stale_maccarone; assuming source is already preprocessed")
else:
    stale_maccarone.enable(
        py_string_matching=False,
        include_pattern="maccarone.*",
    )

from maccarone.loader import enable
