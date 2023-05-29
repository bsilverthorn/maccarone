#!/bin/env bash

# hackishly rewrite the project to use a different name (to support self-hosting)

set -eux

find ./src/maccarone -name "*.py" -print0 | xargs -0 sed -i 's/import maccarone/import stale_maccarone/'
find ./src/maccarone -name "*.py" -print0 | xargs -0 sed -i 's/from maccarone/from stale_maccarone/'

sed -i 's/name = "maccarone"/name = "stale_maccarone"/' pyproject.toml
sed -i 's/local_scheme = "node-and-date"/local_scheme = "no-local-version"/' pyproject.toml

mv src/{maccarone,stale_maccarone}
