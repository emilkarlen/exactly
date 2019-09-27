from exactly_lib.test_case_utils.file_matcher.impl.impl_base_class import FileMatcherImplBase
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel


class FileMatcherThatMatchesAnyFileWhosNameStartsWith(FileMatcherImplBase):

    def __init__(self, prefix_of_name_for_match: str):
        self._prefix_of_name_for_match = prefix_of_name_for_match

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return 'Matches files beginning with ' + self._prefix_of_name_for_match

    def matches(self, model: FileMatcherModel) -> bool:
        return model.path.primitive.name.startswith(self._prefix_of_name_for_match)
