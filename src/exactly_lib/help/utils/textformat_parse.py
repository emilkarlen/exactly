from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs


class TextParser:
    def __init__(self,
                 format_map: dict):
        self.format_map = format_map

    def format(self, s: str) -> str:
        """
        Formats the given string using the format map given in the constructor.
        """
        return s.format_map(self.format_map)

    def fnap(self, s: str) -> list:
        """
        1. Text replacements according to `format_map` given to the constructor.
        2. normalize lines
        3. parse result
        """
        return normalize_and_parse(s.format_map(self.format_map))

    def section(self, header: str, paragraphs_text: str) -> docs.Section:
        """
        :param header: Formatted using `self.format`.
        :param paragraphs_text: Parsed using `self.fnap`.
        """
        return docs.section(docs.text(header.format_map(self.format_map)),
                            self.fnap(paragraphs_text))
