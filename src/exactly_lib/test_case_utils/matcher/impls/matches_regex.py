from typing import Optional, Pattern, Match, Set, Sequence

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import str_matcher
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.regex.regex_ddv import RegexDdv, RegexSdv
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MODEL, MatcherAdv, \
    MatcherWTrace
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable


class MatchesRegex(WithCachedTreeStructureDescriptionBase,
                   MatcherWTrace[str]
                   ):
    NAME = ' '.join((
        str_matcher.MATCH_REGEX_OR_GLOB_PATTERN_CHECK_ARGUMENT,
        syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name,
    ))

    def __init__(self,
                 is_full_match: bool,
                 pattern: Pattern[str],
                 ):
        super().__init__()
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

    def matches_w_trace(self, model: str) -> MatchingResult:
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
                 regex: RegexDdv,
                 is_full_match: bool,
                 ):
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
    def validator(self) -> DdvValidator:
        return self._regex.validator()

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return advs.ConstantMatcherAdv(
            MatchesRegex(
                self._is_full_match,
                self._regex.value_of_any_dependency(tcds),
            )
        )


class MatchesRegexSdv(MatcherSdv[str]):
    def __init__(self,
                 regex: RegexSdv,
                 is_full_match: bool,
                 ):
        self._regex = regex
        self._is_full_match = is_full_match

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._regex.references

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        return MatchesRegexDdv(
            self._regex.resolve(symbols),
            self._is_full_match,
        )
