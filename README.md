# ASCII Art Box Drawer

Wraps text in a pure-ASCII border box — single, double, or rounded — with no
wrapping and no third-party dependencies.

```python
from ascii_art_box_drawer import draw_box, Style, STYLES

print(draw_box("hello, world"))
print(draw_box("firm\nspec", style="double"))
print(draw_box("rounded", style="rounded"))

custom = Style(top=("<", ">"), bottom=("<", ">"),
               horizontal=".", vertical=":", name="custom")
print(draw_box("custom", style=custom))
```

## Why this exists

The specific problem: you have a few lines of text and you want a visible
frame around them on a terminal or in a log, using only 7-bit ASCII so it
survives any code page and any transport. Existing box-drawing tools either
pull in Unicode glyphs that get mangled, or bundle a text-wrapping engine
that reflows your carefully-formatted content.

The trade-off: this library draws exactly the lines you give it. It does not
wrap, it does not hyphenate, it does not collapse spaces. The box width is
the width of the widest input line, full stop. That keeps behaviour
deterministic and the implementation tiny.

## The awkward edge

A trailing newline in the input becomes a final empty interior row.
`draw_box("hi")` draws a one-row box; `draw_box("hi\n")` draws a two-row
box whose second row is blank. This is intentional — it matches what you
expect when framing the output of `print`-style code that ends lines with
`\n` — but it is the one behaviour that surprises people who assume trailing
whitespace is trimmed. If you do not want the blank row, strip the input
before passing it in.

CRLF and lone CR are normalised to LF internally, so neither will overwrite
the left border on terminals that honour carriage returns.

## Exports

- `draw_box(text: str, style="single") -> str` — frame `text` and return the
  box as a string with `\n` separators (no trailing newline).
- `Style` — dataclass describing a border character set; pass an instance as
  `style` to use a custom frame.
- `STYLES` — dict of the three registered styles: `"single"`, `"double"`,
  `"rounded"`.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

