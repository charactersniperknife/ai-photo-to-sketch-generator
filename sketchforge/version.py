"""Single source of truth for the package version.

Kept separate so build tooling and the CLI can import it without pulling in
the heavy numpy/opencv import chain.
"""

__version__ = "0.4.2"
__release_channel__ = "beta"
__build_year__ = 2026