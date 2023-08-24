from importlib.metadata import (
    version,
    PackageNotFoundError,
)

try:
    __version__ = version(__name__)
except PackageNotFoundError as error:
    __version__ = "unknown"
