from typing import Optional, Pattern, Match, Set

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import str_matcher
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.regex.regex_ddv import RegexDdv
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatcherDdv, T
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.logic_types import ExpectationType


class MatchesRegex(MatcherWTraceAndNegation[str]):
    NAME = ' '.join((
        str_matcher.REGEX_MATCH_CHECK_ARGUMENT,
        syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name,
    ))

    def __init__(self,
                 expectation_type: ExpectationType,
                 is_full_match: bool,
                 pattern: Pattern[str],
                 ):
        super().__init__()
        self._expectation_type = expectation_type
        self._is_full_match = is_full_match
        self._pattern = pattern
        self._pattern_renderer = custom_details.PatternRenderer(pattern)
        self._expected_detail_renderer = custom_details.expected(
            custom_details.regex_with_config_renderer(
                is_full_match,
                self._pattern_renderer,
            )
        )

    @property
    def name(self) -> str:
        return self.NAME

    @staticmethod
    def new_structure_tree(is_full_match: bool,
                           expected_regex: DetailsRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            MatchesRegex.NAME,
            None,
            (custom_details.regex_with_config_renderer(is_full_match, expected_regex),),
            (),
        )

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(
            self._is_full_match,
            self._pattern_renderer,
        )

    @property
    def option_description(self) -> str:
        return self._name

    @property
    def negation(self) -> MatcherWTraceAndNegation[str]:
        return combinator_matchers.Negation(self)

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        raise NotImplementedError('unsupported')

    def matches_w_trace(self, model: str) -> MatchingResult:
        if self._expectation_type is ExpectationType.NEGATIVE:
            positive_matcher = MatchesRegex(ExpectationType.POSITIVE,
                                            self._is_full_match,
                                            self._pattern)
            return combinator_matchers.Negation(positive_matcher).matches_w_trace(model)
        else:
            return self._matches_positive(model)

    def _matches_positive(self, model: str) -> MatchingResult:
        tb = self._new_tb_with_expected().append_details(
            custom_details.actual(
                custom_details.StringAsSingleLineWithMaxLenDetailsRenderer(model))
        )

        match = self._find_match(model)

        if match is not None:
            tb.append_details(
                custom_details.match(custom_details.PatternMatchRenderer(match))
            )

        return tb.build_result(match is not None)

    def _find_match(self, model: str) -> Optional[Match]:
        if self._is_full_match:
            return self._pattern.fullmatch(model)
        else:
            return self._pattern.search(model)

    def _new_tb_with_expected(self) -> TraceBuilder:
        return TraceBuilder(self.NAME).append_details(self._expected_detail_renderer)


class MatchesRegexDdv(MatcherDdv[str]):
    def __init__(self,
                 expectation_type: ExpectationType,
                 regex: RegexDdv,
                 is_full_match: bool,
                 ):
        self._expectation_type = expectation_type
        self._regex = regex
        self._is_full_match = is_full_match

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._regex.resolving_dependencies()

    def structure(self) -> StructureRenderer:
        return MatchesRegex.new_structure_tree(
            self._is_full_match,
            self._regex.describer(),
        )

    @property
    def validator(self) -> PreOrPostSdsValueValidator:
        return self._regex.validator()

    def value_of_any_dependency(self, tcds: HomeAndSds) -> MatcherWTraceAndNegation[T]:
        return MatchesRegex(
            self._expectation_type,
            self._is_full_match,
            self._regex.value_of_any_dependency(tcds),
        )
