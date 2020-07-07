from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.test_case_utils.string_matcher.impl.base_class import StringMatcherImplBase
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.description_tree import details, renderers


class EmptinessStringMatcher(StringMatcherImplBase):
    NAME = file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT

    @staticmethod
    def new_structure_tree() -> StructureRenderer:
        return renderers.header_only(EmptinessStringMatcher.NAME)

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree()

    def matches_w_trace(self, model: StringModel) -> MatchingResult:
        first_line = self._first_line(model)
        if first_line != '':
            return (
                self._new_tb()
                    .append_details(
                    custom_details.actual(details.String(repr(first_line) + '...'))
                )
                    .build_result(False)
            )
        else:
            return self._new_tb().build_result(True)

    @staticmethod
    def _first_line(file_to_check: StringModel) -> str:
        with file_to_check.as_lines as lines:
            for line in lines:
                return line
        return ''


def sdv() -> StringMatcherSdv:
    return sdv_components.matcher_sdv_from_constant_primitive(EmptinessStringMatcher())
