class TextItem:
    pass


class Paragraph(TextItem):
    def __init__(self,
                 start_on_new_line_blocks: list):
        """
        :param start_on_new_line_blocks: Each element is a text that should start
        on a new line.
        """
        self.start_on_new_line_blocks = start_on_new_line_blocks


class TextItemVisitor:
    def visit(self, text_item: TextItem):
        if isinstance(text_item, Paragraph):
            return self.visit_paragraph(text_item)
        raise ValueError('Unknown TextItem: ' + str(type(text_item)))

    def visit_paragraph(self, paragraph: Paragraph):
        raise NotImplemented()
