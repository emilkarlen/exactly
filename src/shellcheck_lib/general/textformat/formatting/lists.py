from shellcheck_lib.general.textformat.structure.core import Text

from shellcheck_lib.general.textformat.structure.lists import ListType, Separations


class HeaderAndIndentFormat:
    def header_text(self,
                    element_number: int,
                    total_number_of_elements: int,
                    header: Text) -> Text:
        """
        :param element_number: 1, 2, ...
        :param total_number_of_elements: Number of elements in the list
        :param header:
        """
        raise NotImplementedError()

    def following_header_lines_indent(self,
                                      element_number: int,
                                      total_number_of_elements: int) -> str:
        """
        Indentation of lines that are part of the header, but that does not fit on the first line.
        """
        raise NotImplementedError()

    def contents_indent(self,
                        total_number_of_elements: int) -> str:
        raise NotImplementedError()


class ListFormat(tuple):
    def __new__(cls,
                header_and_indent_format: HeaderAndIndentFormat,
                separations: Separations,
                indent_str: str = ''):
        return tuple.__new__(cls, (header_and_indent_format,
                                   separations,
                                   indent_str))

    @property
    def header_format(self) -> HeaderAndIndentFormat:
        return self[0]

    @property
    def separations(self) -> Separations:
        return self[1]

    @property
    def indent_str(self) -> str:
        return self[2]


def list_format_with_indent_str(list_format: ListFormat, indent_str: str) -> ListFormat:
    return ListFormat(list_format.header_format,
                      list_format.separations,
                      indent_str)


def list_format_with_separations(list_format: ListFormat, separations: Separations) -> ListFormat:
    return ListFormat(list_format.header_format,
                      separations,
                      list_format.indent_str)


class HeaderAndIndentFormatWithConstantValueIndentBase(HeaderAndIndentFormat):
    def __init__(self,
                 contents_indent_spaces: int):
        self.contents_indent_str = contents_indent_spaces * ' '

    def contents_indent(self,
                        total_number_of_elements: int) -> str:
        return self.contents_indent_str


class HeaderAndIndentFormatPlain(HeaderAndIndentFormatWithConstantValueIndentBase):
    def __init__(self,
                 contents_indent_spaces: int = 3):
        super().__init__(contents_indent_spaces)

    def header_text(self,
                    element_number: int,
                    total_number_of_elements: int,
                    header: Text) -> Text:
        return header

    def following_header_lines_indent(self,
                                      element_number: int,
                                      total_number_of_elements: int) -> str:
        return ''


class HeaderAndIndentFormatWithMarker(HeaderAndIndentFormatWithConstantValueIndentBase):
    def __init__(self,
                 marker: str,
                 contents_indent_spaces: int = 3):
        super().__init__(contents_indent_spaces)
        self.marker = marker

    def header_text(self,
                    element_number: int,
                    total_number_of_elements: int,
                    header: Text) -> Text:
        return Text(self.marker + ' ' + header.value)

    def following_header_lines_indent(self,
                                      element_number: int,
                                      total_number_of_elements: int) -> str:
        return (len(self.marker) + 1) * ' '


class HeaderAndIndentFormatWithNumbering(HeaderAndIndentFormatWithConstantValueIndentBase):
    def __init__(self,
                 contents_indent_spaces: int = 3):
        super().__init__(contents_indent_spaces)

    def header_text(self,
                    element_number: int,
                    total_number_of_elements: int,
                    header: Text) -> Text:
        return Text(self._prefix(element_number) + header.value)

    def following_header_lines_indent(self,
                                      element_number: int,
                                      total_number_of_elements: int) -> str:
        return len(self._prefix(element_number)) * ' '

    @staticmethod
    def _prefix(element_number: int) -> str:
        return '%d. ' % element_number


class ListFormats(tuple):
    def __new__(cls,
                itemized_list_format: ListFormat = ListFormat(HeaderAndIndentFormatWithMarker('*'),
                                                              Separations(0, 0)),
                ordered_list_format: ListFormat = ListFormat(HeaderAndIndentFormatWithNumbering(),
                                                             Separations(0, 0)),
                variable_list_format: ListFormat = ListFormat(HeaderAndIndentFormatPlain(),
                                                              Separations(0, 0))):
        type_to_format = {
            ListType.ITEMIZED_LIST: itemized_list_format,
            ListType.ORDERED_LIST: ordered_list_format,
            ListType.VARIABLE_LIST: variable_list_format,
        }
        return tuple.__new__(cls, (type_to_format,))

    def for_type(self, list_type: ListType) -> ListFormat:
        return self[0][list_type]
