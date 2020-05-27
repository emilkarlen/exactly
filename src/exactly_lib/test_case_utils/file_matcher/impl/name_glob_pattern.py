from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import file_matcher, str_matcher
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.file_matcher.impl.base_class import FileMatcherDdvImplBase, FileMatcherImplBase
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcherModel, FileMatcherSdv
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherAdv, MODEL
from exactly_lib.util import strings
from exactly_lib.util.description_tree import details, renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.render import strings as string_rendering
from exactly_lib.util.symbol_table import SymbolTable


def parse(token_parser: TokenParser) -> FileMatcherSdv:
    glob_pattern = parse_string.parse_string_from_token_parser(token_parser, _PARSE_STRING_CONFIGURATION)

    return _sdv(glob_pattern)


_PARSE_STRING_CONFIGURATION = parse_string.Configuration(syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.singular_name,
                                                         reference_restrictions=None)


def _sdv(glob_pattern: StringSdv) -> FileMatcherSdv:
    def make_ddv(symbols: SymbolTable) -> FileMatcherDdv:
        return _Ddv(glob_pattern.resolve(symbols))

    return sdv_components.MatcherSdvFromParts(
        glob_pattern.references,
        make_ddv,
    )


class _Ddv(FileMatcherDdvImplBase):
    def __init__(self, glob_pattern: StringDdv):
        self._glob_pattern = glob_pattern

    def structure(self) -> StructureRenderer:
        return _FileMatcherNameGlobPattern.new_structure_tree(
            details.String(strings.Repr(string_rendering.AsToStringObject(self._glob_pattern.describer())))
        )

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return advs.ConstantMatcherAdv(_FileMatcherNameGlobPattern(self._glob_pattern.value_of_any_dependency(tcds)))


class _FileMatcherNameGlobPattern(FileMatcherImplBase):
    """Matches the name (whole path, not just base name) of a path on a shell glob pattern."""

    NAME = file_matcher.NAME_MATCHER_NAME

    _SUB_MATCHER_NAME = ' '.join((
        str_matcher.MATCH_REGEX_OR_GLOB_PATTERN_CHECK_ARGUMENT,
        syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.singular_name,
    ))

    def __init__(self, glob_pattern: str):
        super().__init__()
        self._glob_pattern = glob_pattern
        self._renderer_of_expected = custom_details.expected(
            self._sub_matcher_renderer(details.String(strings.Repr(glob_pattern)))
        )

    @property
    def glob_pattern(self) -> str:
        return self._glob_pattern

    @property
    def name(self) -> str:
        return file_matcher.NAME_MATCHER_NAME

    @staticmethod
    def _sub_matcher_renderer(glob_pattern: DetailsRenderer) -> DetailsRenderer:
        return details.HeaderAndValue(
            _FileMatcherNameGlobPattern._SUB_MATCHER_NAME,
            glob_pattern,
        )

    @staticmethod
    def new_structure_tree(glob_pattern: DetailsRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            _FileMatcherNameGlobPattern.NAME,
            None,
            (_FileMatcherNameGlobPattern._sub_matcher_renderer(glob_pattern),),
            (),
        )

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(details.String(strings.Repr(self._glob_pattern)))

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        tb = self.__tb_with_expected().append_details(
            custom_details.actual(
                custom_details.PathDdvAndPrimitiveIfRelHomeAsIndentedDetailsRenderer(model.path.describer)
            )
        )
        return tb.build_result(model.path.primitive.match(self._glob_pattern))

    def __tb_with_expected(self) -> TraceBuilder:
        return TraceBuilder(self.NAME).append_details(self._renderer_of_expected)
