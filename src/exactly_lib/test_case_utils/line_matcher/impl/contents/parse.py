from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.tcfs.ddv_validation import DdvValidator
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case_utils.line_matcher.impl.contents.string_model import StringModel
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine, LineMatcherSdv, LineMatcherDdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherAdv, MatcherWTrace, MODEL
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv, StringMatcherDdv, StringMatcherAdv, \
    StringMatcher
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.symbol_table import SymbolTable


class _Parser(ParserFromTokens[LineMatcherSdv]):
    def parse(self, token_parser: TokenParser) -> LineMatcherSdv:
        from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
        string_matcher_parser = parse_string_matcher.parsers(False).simple
        contents_matcher = string_matcher_parser.parse_from_token_parser(token_parser)
        return _sdv(contents_matcher)


PARSER = _Parser()


def _sdv(string_matcher: StringMatcherSdv) -> LineMatcherSdv:
    def make_ddv(symbols: SymbolTable) -> LineMatcherDdv:
        return _LineContentsMatcherDdv(string_matcher.resolve(symbols))

    return sdv_components.MatcherSdvFromParts(
        string_matcher.references,
        make_ddv,
    )


class _LineContentsMatcherDdv(MatcherDdv[LineMatcherLine]):
    def __init__(self, contents_matcher: StringMatcherDdv):
        self._contents_matcher = contents_matcher

    def structure(self) -> StructureRenderer:
        return _LineContentsMatcher.new_structure_tree(
            self._contents_matcher.structure()
        )

    @property
    def validator(self) -> DdvValidator:
        return self._contents_matcher.validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return _LineContentsMatcherAdv(self._contents_matcher.value_of_any_dependency(tcds))


class _LineContentsMatcherAdv(MatcherAdv[LineMatcherLine]):
    def __init__(self, contents_matcher: StringMatcherAdv):
        self._contents_matcher = contents_matcher

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        return _LineContentsMatcher(environment, self._contents_matcher.primitive(environment))


class _LineContentsMatcher(MatcherImplBase[LineMatcherLine]):
    NAME = ' '.join((
        line_matcher.CONTENTS_MATCHER_NAME,
        syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.singular_name,
    ))

    def __init__(self,
                 environment: ApplicationEnvironment,
                 contents_matcher: StringMatcher,
                 ):
        super().__init__()
        self._environment = environment
        self._contents_matcher = contents_matcher

    @staticmethod
    def new_structure_tree(string_matcher: StructureRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            _LineContentsMatcher.NAME,
            None,
            (),
            (string_matcher,),
        )

    @property
    def name(self) -> str:
        return self.NAME

    def matches_w_trace(self, model: LineMatcherLine) -> MatchingResult:
        string_matcher_model = StringModel(
            model[1],
            self._environment.tmp_files_space,
        )
        matcher_result = self._contents_matcher.matches_w_trace(string_matcher_model)
        tb = TraceBuilder(self.NAME).append_child(matcher_result.trace)
        return tb.build_result(matcher_result.value)

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(
            self._contents_matcher.structure()
        )