from shellcheck_lib.general.textformat.structure.core import ParagraphItem, Text


class Paragraph(ParagraphItem):
    def __init__(self,
                 start_on_new_line_blocks: list):
        """
        :param start_on_new_line_blocks: [Text] Each element is a text that should start
        on a new line.
        """
        self.start_on_new_line_blocks = start_on_new_line_blocks


def para(text: str) -> Paragraph:
    return Paragraph([Text(text)])


def single_para(text: str) -> list:
    return [para(text)]
