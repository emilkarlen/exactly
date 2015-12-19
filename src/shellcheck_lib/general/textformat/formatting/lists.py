from shellcheck_lib.general.textformat.structure.core import Text

from shellcheck_lib.general.textformat.structure.lists import ListType


class Separations(tuple):
    def __new__(cls,
                num_blank_lines_between_elements: int,
                num_blank_lines_between_header_and_value: int):
        return tuple.__new__(cls, (num_blank_lines_between_elements,
                                   num_blank_lines_between_header_and_value))

    @property
    def num_blank_lines_between_elements(self) -> int:
        return self[0]

    @property
    def num_blank_lines_between_header_and_value(self) -> int:
        return self[1]


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

    def value_indent(self,
                     total_number_of_elements: int) -> str:
        raise NotImplementedError()


class ListFormat(tuple):
    def __new__(cls,
                header_and_indent_format: HeaderAndIndentFormat,
                separations: Separations):
        return tuple.__new__(cls, (header_and_indent_format,
                                   separations))

    @property
    def header_and_indent_format(self) -> HeaderAndIndentFormat:
        return self[0]

    @property
    def separations(self) -> Separations:
        return self[1]


class HeaderAndIndentFormatWithConstantValueIndentBase(HeaderAndIndentFormat):
    def __init__(self,
                 value_indent_spaces: int):
        self.value_indent_str = value_indent_spaces * ' '

    def value_indent(self,
                     total_number_of_elements: int) -> str:
        return self.value_indent_str


class HeaderAndIndentFormatWithMarker(HeaderAndIndentFormatWithConstantValueIndentBase):
    def __init__(self,
                 marker: str,
                 value_indent_spaces: int = 3):
        super().__init__(value_indent_spaces)
        self.marker = marker

    def header_text(self,
                    element_number: int,
                    total_number_of_elements: int,
                    header: Text) -> Text:
        return Text(self.marker + ' ' + header.value)


class HeaderAndIndentFormatPlain(HeaderAndIndentFormatWithConstantValueIndentBase):
    def __init__(self,
                 value_indent_spaces: int = 3):
        super().__init__(value_indent_spaces)

    def header_text(self,
                    element_number: int,
                    total_number_of_elements: int,
                    header: Text) -> Text:
        return header


class HeaderAndIndentFormatWithNumbering(HeaderAndIndentFormatWithConstantValueIndentBase):
    def __init__(self,
                 value_indent_spaces: int = 3):
        super().__init__(value_indent_spaces)

    def header_text(self,
                    element_number: int,
                    total_number_of_elements: int,
                    header: Text) -> Text:
        return Text('%d. %s' % (element_number, header.value))


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
