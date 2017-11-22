from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs


class TextParser:
    def __init__(self,
                 format_map: dict = None):
        self.format_map = {} if format_map is None else format_map

    def format(self, s: str, extra: dict = None) -> str:
        """
        Formats the given string using the format map given in the constructor.
        """
        if extra is None:
            d = self.format_map
        else:
            d = dict(self.format_map)
            d.update(extra)
        return s.format_map(d)

    def text(self, s: str, extra: dict = None) -> docs.Text:
        return docs.text(self.format(s, extra))

    def para(self, s: str, extra: dict = None) -> docs.ParagraphItem:
        return docs.para(self.format(s, extra))

    def paras(self, s: str, extra: dict = None) -> list:
        return docs.paras(self.format(s, extra))

    def fnap(self, s: str, extra: dict = None) -> list:
        """
        1. Text replacements according to `format_map` given to the constructor.
        2. normalize lines
        3. parse result
        :rtype: [`ParagraphItem`]
        """
        return normalize_and_parse(self.format(s, extra))

    def paragraph_items(self, s: str, extra: dict = None) -> list:
        return self.fnap(self.format(s, extra))

    def section(self, header_or_text, paragraphs_text: str, extra: dict = None) -> docs.Section:
        """
        :param header_or_text: If a `str` it is formatted using `self.format`.
        :param paragraphs_text: Parsed using `self.fnap`.
        """
        header = header_or_text
        if not isinstance(header_or_text, docs.Text):
            header = docs.text(self.format(header_or_text, extra))
        return docs.section(header, self.fnap(paragraphs_text, extra))

    def section_contents(self, paragraphs_text: str, extra: dict = None) -> docs.SectionContents:
        """
        :param paragraphs_text: Parsed using `self.fnap`.
        """
        return docs.section_contents(self.fnap(paragraphs_text, extra))
