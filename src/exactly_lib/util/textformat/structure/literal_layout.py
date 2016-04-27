from exactly_lib.util.textformat.structure.core import ParagraphItem


class LiteralLayout(ParagraphItem):
    def __init__(self,
                 literal_text: str):
        self._literal_text = literal_text

    @property
    def literal_text(self) -> str:
        return self._literal_text
