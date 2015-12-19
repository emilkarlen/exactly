class Text(tuple):
    def __new__(cls,
                value: str):
        return tuple.__new__(cls, (value,))

    @property
    def value(self) -> str:
        return self[0]


class ParagraphItem:
    """
    An item that is an element of a paragraph-level sequence of elements.
    """
    pass
