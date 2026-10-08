"""Unit tests for :mod:`ascii_art_box_drawer.core`.

Every test here exercises behaviour the implementation actually claims to
support. We deliberately avoid inventing requirements (no wrapping, no
width caps, no colour) that ``draw_box`` does not implement.
"""

import unittest

from ascii_art_box_drawer import (
    Style,
    STYLES,
    draw_box,
)


class DrawBoxSingleTests(unittest.TestCase):
    """Happy-path and structural tests for the default single style."""

    def test_single_line(self):
        out = draw_box("hi")
        self.assertEqual(out, "+--+\n|hi|\n+--+")

    def test_multiline_uses_widest_line_as_width(self):
        out = draw_box("a\nbb\nccc")
        self.assertEqual(
            out,
            "+---+\n|a  |\n|bb |\n|ccc|\n+---+",
        )

    def test_empty_string_draws_visible_empty_box(self):
        out = draw_box("")
        self.assertEqual(out, "++\n||\n++")

    def test_returns_str_without_trailing_newline(self):
        # The contract is explicit: no trailing newline. Callers add one
        # via print if they want it.
        out = draw_box("x")
        self.assertIsInstance(out, str)
        self.assertFalse(out.endswith("\n"))

    def test_result_line_count_is_body_plus_two(self):
        text = "one\ntwo\nthree"
        out = draw_box(text)
        self.assertEqual(len(out.split("\n")), len(text.split("\n")) + 2)


class DrawBoxStyleTests(unittest.TestCase):
    """Verify each registered style produces the documented corner glyphs."""

    def test_double_style(self):
        out = draw_box("hi", style="double")
        self.assertEqual(out, "H==H\n|hi|\nH==H")

    def test_rounded_style(self):
        out = draw_box("hi", style="rounded")
        # Forward-slash top corners, back-slash bottom corners.
        self.assertEqual(out, "/--\\\n|hi|\n\\--/")

    def test_style_instance_passes_through(self):
        custom = Style(
            top=("<", ">"),
            bottom=("<", ">"),
            horizontal=".",
            vertical=":",
            name="custom",
        )
        out = draw_box("hi", style=custom)
        self.assertEqual(out, "<..>\n:hi:\n<..>")

    def test_unknown_style_name_raises_valueerror(self):
        with self.assertRaises(ValueError):
            draw_box("hi", style="fancy")

    def test_non_str_non_style_raises_typeerror(self):
        with self.assertRaises(TypeError):
            draw_box("hi", style=42)


class DrawBoxEdgeCaseTests(unittest.TestCase):
    """Awkward inputs the implementation explicitly handles."""

    def test_trailing_newline_becomes_final_empty_row(self):
        # Documented behaviour: a trailing newline yields a blank interior
        # row, so the box has one more body line than the stripped text.
        out = draw_box("hi\n")
        self.assertEqual(out, "+--+\n|hi|\n|  |\n+--+")

    def test_crlf_normalised_to_lf(self):
        # CRLF must not corrupt the left border; we treat it as LF.
        out = draw_box("a\r\nb")
        self.assertEqual(out, "+-+\n|a|\n|b|\n+-+")

    def test_lone_cr_normalised_to_lf(self):
        out = draw_box("a\rb")
        self.assertEqual(out, "+-+\n|a|\n|b|\n+-+")

    def test_leading_blank_line_preserved(self):
        out = draw_box("\nhi")
        self.assertEqual(out, "+--+\n|  |\n|hi|\n+--+")

    def test_internal_blank_line_preserved(self):
        out = draw_box("hi\n\nthere")
        self.assertEqual(out, "+-----+\n|hi   |\n|     |\n|there|\n+-----+")

    def test_preserves_leading_spaces_in_content(self):
        # We do not collapse or trim whitespace; indentation is part of the
        # text and counts toward the visible width.
        out = draw_box("  indented")
        self.assertEqual(out, "+----------+\n|  indented|\n+----------+")

    def test_non_str_text_raises_typeerror(self):
        with self.assertRaises(TypeError):
            draw_box(123)


class StylesRegistryTests(unittest.TestCase):
    """Guard the public STYLES mapping so renames are caught by tests."""

    def test_registered_style_names(self):
        self.assertEqual(set(STYLES), {"single", "double", "rounded"})

    def test_each_style_has_consistent_corner_count(self):
        for name, s in STYLES.items():
            self.assertEqual(len(s.top), 2, name)
            self.assertEqual(len(s.bottom), 2, name)
            self.assertEqual(len(s.horizontal), 1, name)
            self.assertEqual(len(s.vertical), 1, name)


if __name__ == "__main__":
    unittest.main()
