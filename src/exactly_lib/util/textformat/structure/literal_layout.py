from typing import Optional

from exactly_lib.util.textformat.structure.core import ParagraphItem


class LiteralLayout(ParagraphItem):
    def __init__(self,
                 literal_text: str,
                 class_: Optional[str] = None,
                 ):
        self._literal_text = literal_text
        self._class_ = class_

    @property
    def literal_text(self) -> str:
        return self._literal_text

    @property
    def class_(self) -> Optional[str]:
        return self._class_
