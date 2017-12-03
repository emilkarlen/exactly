from exactly_lib.help_texts.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.util.name import Name
from exactly_lib.util.textformat.structure.core import Text, StringText


class EntityTypeNames(tuple):
    def __new__(cls,
                identifier: str,
                name: Name):
        return tuple.__new__(cls, (name,
                                   identifier))

    @property
    def name(self) -> Name:
        return self[0]

    @property
    def identifier(self) -> str:
        return self[1]


class SingularNameAndCrossReferenceId:
    def __init__(self,
                 singular_name: str,
                 single_line_description_str: str,
                 cross_reference_target: CrossReferenceId):
        self._cross_reference_target = cross_reference_target
        self._single_line_description_str = single_line_description_str
        self._singular_name = singular_name

    @property
    def singular_name(self) -> str:
        return self._singular_name

    @property
    def singular_name_text(self) -> StringText:
        return StringText(self._singular_name)

    @property
    def single_line_description_str(self) -> str:
        return self._single_line_description_str

    @property
    def single_line_description(self) -> Text:
        return StringText(self._single_line_description_str)

    @property
    def cross_reference_target(self) -> CrossReferenceId:
        return self._cross_reference_target


class SingularAndPluralNameAndCrossReferenceId(SingularNameAndCrossReferenceId):
    def __init__(self,
                 name: Name,
                 single_line_description_str: str,
                 cross_reference_target: CrossReferenceId):
        super().__init__(name.singular,
                         single_line_description_str,
                         cross_reference_target)
        self._name = name

    @property
    def name(self) -> Name:
        return self._name

    @property
    def plural_name(self) -> str:
        return self.name.plural


def cross_reference_id_list(singular_name_and_cross_reference_id_iterable) -> list:
    return [x.cross_reference_target
            for x in singular_name_and_cross_reference_id_iterable]
