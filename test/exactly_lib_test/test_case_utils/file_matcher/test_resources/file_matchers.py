from exactly_lib.test_case_utils.file_matcher.impl.base_class import FileMatcherImplBase
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.description_tree import renderers
from exactly_lib_test.type_system.logic.test_resources import matching_result


class FileMatcherTestImplBase(FileMatcherImplBase):
    @property
    def name(self) -> str:
        return str(type(self))

    def _structure(self) -> StructureRenderer:
        return renderers.header_only(self.name)


class IsRegularFileMatcher(FileMatcherTestImplBase):
    def __init__(self):
        super().__init__()

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return matching_result.of(
            model.file_type_access.is_type(FileType.REGULAR)
        )


class IsDirectoryMatcher(FileMatcherTestImplBase):
    def __init__(self):
        super().__init__()

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return matching_result.of(
            model.file_type_access.is_type(FileType.DIRECTORY)
        )


class BaseNameStartsWithMatcher(FileMatcherTestImplBase):
    def __init__(self, base_name_prefix: str):
        super().__init__()
        self._base_name_prefix = base_name_prefix

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return matching_result.of(
            model.path.primitive.name.startswith(self._base_name_prefix)
        )
