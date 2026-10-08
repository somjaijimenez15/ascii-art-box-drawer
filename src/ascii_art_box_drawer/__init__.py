"""ASCII Art Box Drawer — wrap text in pure-ASCII border boxes.

A tiny standard-library-only library for framing text inside one of three
border styles: single, double, or rounded. The whole public API lives in
:mod:`ascii_art_box_drawer.core`; this package init re-exports it so users
can write ``from ascii_art_box_drawer import draw_box`` without descending
into internals.
"""

from .core import (
    Style,
    draw_box,
    STYLES,
)

__all__ = [
    "Style",
    "draw_box",
    "STYLES",
]

__version__ = "1.0.0"
