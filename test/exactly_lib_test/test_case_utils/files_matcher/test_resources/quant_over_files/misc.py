from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherModel


class FileMatcherThatMatchesAnyFileWhosNameStartsWith(FileMatcher):

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return 'Matches files beginning with ' + self._prefix_of_name_for_match

    def __init__(self, prefix_of_name_for_match: str):
        self._prefix_of_name_for_match = prefix_of_name_for_match

    def matches(self, model: FileMatcherModel) -> bool:
        return model.path.primitive.name.startswith(self._prefix_of_name_for_match)
