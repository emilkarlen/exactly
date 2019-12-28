from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.description_tree import custom_details, custom_renderers
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers, sdv_components
from exactly_lib.test_case_utils.string_matcher.impl.base_class import StringMatcherImplBase
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.type_system.logic.string_matcher import StringMatcher
from exactly_lib.util.description_tree import details, renderers
from exactly_lib.util.logic_types import ExpectationType


class EmptinessStringMatcher(StringMatcherImplBase):
    NAME = file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT

    @staticmethod
    def new_structure_tree(expectation_type: ExpectationType) -> StructureRenderer:
        positive = renderers.header_only(EmptinessStringMatcher.NAME)
        return (
            positive
            if expectation_type is ExpectationType.POSITIVE
            else
            custom_renderers.negation(positive)
        )

    def __init__(self, expectation_type: ExpectationType):
        super().__init__()
        self._expectation_type = expectation_type

    @property
    def name(self) -> str:
        return file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._expectation_type)

    @property
    def negation(self) -> StringMatcher:
        return combinator_matchers.Negation(self)

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        if self._expectation_type is ExpectationType.NEGATIVE:
            return combinator_matchers.Negation(EmptinessStringMatcher(ExpectationType.POSITIVE)).matches_w_trace(model)
        else:
            return self._matches_positive(model)

    def _matches_positive(self, model: FileToCheck) -> MatchingResult:
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
    def _first_line(file_to_check: FileToCheck) -> str:
        with file_to_check.lines() as lines:
            for line in lines:
                return line
        return ''


def sdv(expectation_type: ExpectationType) -> StringMatcherSdv:
    return StringMatcherSdv(
        sdv_components.matcher_sdv_from_constant_primitive(EmptinessStringMatcher(expectation_type))
    )
