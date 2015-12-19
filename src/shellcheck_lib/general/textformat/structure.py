class ParagraphItem:
    """
    An item that is an element of a paragraph-level sequence of elements.
    """
    pass


class Text(tuple):
    def __new__(cls,
                value: str):
        return tuple.__new__(cls, (value,))

    @property
    def value(self) -> str:
        return self[0]


class Paragraph(ParagraphItem):
    def __init__(self,
                 start_on_new_line_blocks: list):
        """
        :param start_on_new_line_blocks: [Text] Each element is a text that should start
        on a new line.
        """
        self.start_on_new_line_blocks = start_on_new_line_blocks


class ParagraphItemVisitor:
    def visit(self, item: ParagraphItem):
        if isinstance(item, Paragraph):
            return self.visit_paragraph(item)
        raise ValueError('Unknown {}: {}'.format(ParagraphItem.__name__) + str(type(item)))

    def visit_paragraph(self, paragraph: Paragraph):
        raise NotImplemented()
