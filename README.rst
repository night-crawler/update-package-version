UPDATE PACKAGE VERSION
----------------------

This package provides a python executable that delivers a path-wide version bump feature.
It reads `~/.update-package-version.yml` file for root paths from which it should start its recursive package search.

Package versions are updated using the broadest clause widely across those default patterns:
 - `Pipfile`
 - `requirements.txt`
 - `requirements/*.txt`
 
