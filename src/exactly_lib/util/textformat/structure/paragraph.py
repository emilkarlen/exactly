from exactly_lib.util.textformat.structure.core import ParagraphItem


class Paragraph(ParagraphItem):
    def __init__(self,
                 start_on_new_line_blocks: list):
        """
        :type start_on_new_line_blocks: [Text]
        :param start_on_new_line_blocks: Each element is a text that should start
        on a new line.
        """
        self.start_on_new_line_blocks = start_on_new_line_blocks

    def __str__(self):
        return '{}({})'.format(str(type(self)),
                               repr(self.start_on_new_line_blocks))
