from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.impls.types.matcher.impls import sdv_components
from exactly_lib.impls.types.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.impls.types.string_source.constant_str import string_source
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.line_matcher import LineMatcherDdv, LineMatcherSdv
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherAdv, StringMatcherDdv, StringMatcherSdv
from exactly_lib.type_val_prims.description.trace_building import TraceBuilder
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace, MODEL
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.type_val_prims.matcher.string_matcher import StringMatcher
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.symbol_table import SymbolTable


class _Parser(ParserFromTokens[LineMatcherSdv]):
    def parse(self, token_parser: TokenParser) -> LineMatcherSdv:
        from exactly_lib.impls.types.string_matcher import parse_string_matcher
        string_matcher_parser = parse_string_matcher.parsers(False).simple
        contents_matcher = string_matcher_parser.parse_from_token_parser(token_parser)
        return sdv(contents_matcher)


PARSER = _Parser()


def sdv(string_matcher: StringMatcherSdv) -> LineMatcherSdv:
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
        string_matcher_model = string_source(
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
