from exactly_lib.util.textformat.structure.core import Text, StringText, CrossReferenceTarget


class SeeAlsoTarget:
    """
    A target that can be presented as a see-also item
    """
    pass


class CrossReferenceId(CrossReferenceTarget, SeeAlsoTarget):
    """
    A part of the help text that can be referred to.

    The base class for all cross references used by Exactly.

    Supports equality.
    """

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self._eq_object_of_same_type(other)

    def _eq_object_of_same_type(self, other):
        raise NotImplementedError('abstract method')


class Name(tuple):
    def __new__(cls,
                singular: str,
                plural: str):
        return tuple.__new__(cls, (singular, plural))

    @property
    def singular(self) -> str:
        return self[0]

    @property
    def plural(self) -> str:
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
