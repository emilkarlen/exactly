class Description(tuple):
    def __new__(cls,
                single_line_description: str,
                rest: list):
        """
        :param single_line_description: Mandatory short description.
        :param rest: [ParagraphItem]
        """
        return tuple.__new__(cls, (single_line_description, rest))

    @property
    def single_line_description(self) -> str:
        return self[0]

    @property
    def rest(self) -> list:
        """
        :return: [ParagraphItem]
        """
        return self[1]


def single_line_description(line: str) -> Description:
    return Description(line, [])
