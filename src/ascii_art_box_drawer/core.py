"""Core implementation of the ASCII Art Box Drawer.

Design decisions, stated plainly so the behaviour is not a surprise:

1. **No wrapping.** The caller is responsible for line length. ``draw_box``
   does not insert hard wraps, does not hyphenate, does not collapse runs of
   spaces. Wrapping is a separate concern and conflating it with framing is
   how framing libraries grow extra heads. If a line is wider than the
   terminal, that is the caller's problem.

2. **Box width follows the widest line, verbatim.** We split the text on
   ``\n`` and measure each resulting line with ``len`` — no tab expansion,
   no East-Asian-width awareness. Every line is padded on the right with
   spaces so the right border lines up. We pad with spaces, never with the
   fill character, so the interior always reads as plain text.

3. **Trailing newline is preserved as a final empty line.** If the input
   ends with ``\n`` we treat that as "the user wants a blank row at the
   bottom", which is what you would expect when framing a paragraph that
   was produced by ``print``-style code. An input of ``"hello\n"`` draws a
   box whose interior is two rows: ``hello`` and an empty row. An input of
   ``"hello"`` draws a one-row box. This is the one ambiguous edge in the
   spec; we picked this reading because it is the least surprising when
   you pipe real text in.

4. **CRLF is normalised to LF.** Carriage returns would corrupt the left
   border on terminals that honour them, so they are stripped up front.

5. **Borders are pure ASCII.** Single uses ``-|+``, double uses ``=|H``,
   rounded uses ``-|/`` (slash corners). The corner characters are chosen so
   the visual style is recognisable even on a 7-bit terminal with no
   Unicode support. We deliberately avoid Unicode box-drawing glyphs
   because the whole point of this library is that it works anywhere.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class Style:
    """A complete border character set.

    Attributes
    ----------
    top:
        ``(tl, tr)`` — top-left and top-right corner glyphs.
    bottom:
        ``(bl, br)`` — bottom-left and bottom-right corner glyphs.
    horizontal:
        The glyph used for the top and bottom edges between corners.
    vertical:
        The glyph used for the left and right edges.
    name:
        Human-readable label, mainly useful for error messages.
    """

    top: Tuple[str, str]
    bottom: Tuple[str, str]
    horizontal: str
    vertical: str
    name: str


# The three supported styles. Keys are the strings the public API accepts.
STYLES: Dict[str, Style] = {
    "single": Style(
        top=("+", "+"),
        bottom=("+", "+"),
        horizontal="-",
        vertical="|",
        name="single",
    ),
    "double": Style(
        top=("H", "H"),
        bottom=("H", "H"),
        horizontal="=",
        vertical="|",
        name="double",
    ),
    "rounded": Style(
        # Forward slashes read as rounded corners on a 7-bit terminal and
        # avoid any glyph that could be mangled by code-page translation.
        top=("/", "\\"),
        bottom=("\\", "/"),
        horizontal="-",
        vertical="|",
        name="rounded",
    ),
}


def _resolve_style(style: object) -> Style:
    """Coerce a user-supplied style argument into a :class:`Style`.

    Accepts a registered style name (``"single"``, ``"double"``,
    ``"rounded"``) or a :class:`Style` instance passed through unchanged.
    Raises :class:`ValueError` for anything else so callers get a clear,
    early failure rather than a confusing ``KeyError`` deeper in.
    """
    if isinstance(style, Style):
        return style
    if isinstance(style, str):
        try:
            return STYLES[style]
        except KeyError:
            raise ValueError(
                f"unknown style {style!r}; "
                f"expected one of {sorted(STYLES)} or a Style instance"
            ) from None
    raise TypeError(
        f"style must be a str or Style instance, got {type(style).__name__}"
    )


def _split_lines(text: str) -> list:
    """Split ``text`` into the exact interior rows the box will contain.

    CRLF is normalised to LF first so carriage returns never eat the left
    border. A trailing newline is preserved as a final empty row, which is
    the documented behaviour for paragraph-style input.
    """
    # Normalise CRLF (and a lone trailing CR) to LF before splitting so the
    # left border is never overwritten by a carriage return on the terminal.
    normalised = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalised.split("\n")


def draw_box(text: str, style="single") -> str:
    """Frame ``text`` inside a pure-ASCII box.

    Parameters
    ----------
    text:
        The content to frame. May contain ``\n`` line breaks; each line is
        drawn verbatim with no wrapping. A trailing newline becomes a final
        empty interior row. If ``text`` is empty a one-row empty box is
        drawn — i.e. an empty string still produces a visible box.
    style:
        Either one of the registered names ``"single"``, ``"double"``,
        ``"rounded"`` or a :class:`Style` instance. Defaults to
        ``"single"``.

    Returns
    -------
    str
        The framed text as a single string with ``\n`` line separators. The
        result never ends with a trailing newline; callers can add one with
        ``print`` if they want one.

    Raises
    ------
    TypeError
        If ``text`` is not a :class:`str`.
    ValueError
        If ``style`` is an unknown name.
    TypeError
        If ``style`` is neither a name nor a :class:`Style`.
    """
    if not isinstance(text, str):
        raise TypeError(
            f"text must be a str, got {type(text).__name__}"
        )

    resolved = _resolve_style(style)
    lines = _split_lines(text)
    width = max(len(line) for line in lines)

    h = resolved.horizontal
    v = resolved.vertical
    tl, tr = resolved.top
    bl, br = resolved.bottom

    top_edge = tl + h * width + tr
    bottom_edge = bl + h * width + br
    body_rows = [f"{v}{line.ljust(width)}{v}" for line in lines]

    return "\n".join([top_edge, *body_rows, bottom_edge])
