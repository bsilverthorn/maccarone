#!/bin/env bash

set -eux

find ./src/maccarone -name "*.py" -print0 | xargs -0 sed -i 's/import maccarone/import stale_maccarone/'
find ./src/maccarone -name "*.py" -print0 | xargs -0 sed -i 's/from maccarone/from stale_maccarone/'

sed -i 's/name = "maccarone"/name = "stale_maccarone"/' pyproject.toml
