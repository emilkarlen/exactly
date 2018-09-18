from exactly_lib.util.textformat.constructor.text import CrossReferenceTextConstructor


class ConstructionEnvironment(tuple):
    def __new__(cls,
                cross_ref_text_constructor: CrossReferenceTextConstructor,
                construct_simple_header_value_lists_as_tables: bool = False):
        return tuple.__new__(cls, (cross_ref_text_constructor,
                                   construct_simple_header_value_lists_as_tables))

    @property
    def cross_ref_text_constructor(self) -> CrossReferenceTextConstructor:
        return self[0]

    @property
    def construct_simple_header_value_lists_as_tables(self) -> bool:
        return self[1]
