from typing import List, Callable, Any, Mapping, Optional

from exactly_lib.util.string import StringFormatter
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem


class TextParser:
    def __init__(self, format_map: Optional[Mapping[str, Any]] = None):
        self._string_formatter = StringFormatter(format_map)

    def format(self, template: str, extra: Optional[Mapping[str, Any]] = None,
               ) -> str:
        """
        Formats the given string using the format map given in the constructor.
        """
        return self._string_formatter.format(template, extra)

    def text(self, s: str, extra: Optional[Mapping[str, Any]] = None,
             ) -> docs.StringText:
        return docs.string_text(self.format(s, extra))

    def para(self, s: str, extra: Optional[Mapping[str, Any]] = None,
             ) -> docs.ParagraphItem:
        return docs.para(self.format(s, extra))

    def paras(self, s: str, extra: Optional[Mapping[str, Any]] = None,
              ) -> List[ParagraphItem]:
        return docs.paras(self.format(s, extra))

    def fnap(self, s: str, extra: Optional[Mapping[str, Any]] = None,
             ) -> List[ParagraphItem]:
        """
        1. Text replacements according to `format_map` given to the constructor.
        2. normalize lines
        3. parse result
        """
        return normalize_and_parse(self.format(s, extra))

    def fnap__fun(self, s: str, extra: Optional[Mapping[str, Any]] = None,
                  ) -> Callable[[], List[ParagraphItem]]:
        """A variant of fnap."""

        def ret_val() -> List[ParagraphItem]:
            return normalize_and_parse(self.format(s, extra))

        return ret_val

    def paragraph_items(self, s: str, extra: Optional[Mapping[str, Any]] = None,
                        ) -> List[ParagraphItem]:
        return self.fnap(self.format(s, extra))

    def section(self,
                header_or_text,
                paragraphs_text: str,
                extra: Optional[Mapping[str, Any]] = None) -> docs.Section:
        """
        :param header_or_text: If a `str` it is formatted using `self.format`.
        :param paragraphs_text: Parsed using `self.fnap`.
        """
        header = header_or_text
        if not isinstance(header_or_text, docs.Text):
            header = docs.text(self.format(header_or_text, extra))
        return docs.section(header, self.fnap(paragraphs_text, extra))

    def section_contents(self,
                         paragraphs_text: str,
                         extra: Optional[Mapping[str, Any]] = None,
                         ) -> docs.SectionContents:
        """
        :param paragraphs_text: Parsed using `self.fnap`.
        """
        return docs.section_contents(self.fnap(paragraphs_text, extra))
