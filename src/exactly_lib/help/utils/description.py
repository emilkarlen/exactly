from exactly_lib.util.textformat.structure.core import Text


class Description(tuple):
    def __new__(cls,
                single_line_description: Text,
                rest_paragraphs: list):
        """
        :param single_line_description: Mandatory short description.
        :param rest_paragraphs: [ParagraphItem]
        """
        return tuple.__new__(cls, (single_line_description,
                                   rest_paragraphs))

    @property
    def single_line_description(self) -> Text:
        return self[0]

    @property
    def rest(self) -> list:
        """
        :return: [ParagraphItem]
        """
        return self[1]


def single_line_description(line: str) -> Description:
    return Description(Text(line), [])
