from typing import Sequence

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.line_matcher import LineMatcherSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.line_matcher.model_construction import original_and_model_iter_from_file_line_iter
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.type_system.description.tree_structured import StructureRenderer, WithTreeStructureDescription
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherAdv, LineMatcherDdv
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, ApplicationEnvironment
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv, StringTransformer, \
    StringTransformerModel, StringTransformerAdv
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.symbol_table import SymbolTable


def parse_filter(parser: TokenParser) -> StringTransformerSdv:
    line_matcher = parse_line_matcher.parse_line_matcher_from_token_parser(parser)
    return _StringTransformerSelectSdv(line_matcher)


class _StringTransformerSelectSdv(StringTransformerSdv):
    def __init__(self, line_matcher_sdv: LineMatcherSdv):
        self.line_matcher_sdv = line_matcher_sdv

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return _SelectStringTransformerDdv(self.line_matcher_sdv.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.line_matcher_sdv.references


class _SelectStringTransformerDdv(StringTransformerDdv):
    """
    Keeps lines matched by a given Line Matcher
    and discards lines not matched.
    """

    def __init__(self, line_matcher: LineMatcherDdv):
        self._line_matcher = line_matcher

    def structure(self) -> StructureRenderer:
        return _SelectStringTransformer.new_structure_tree(self._line_matcher)

    def validator(self) -> DdvValidator:
        return self._line_matcher.validator

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerAdv:
        return _SelectStringTransformerAdv(self._line_matcher.value_of_any_dependency(tcds))


class _SelectStringTransformerAdv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self, line_matcher: LineMatcherAdv):
        self._line_matcher = line_matcher

    def applier(self, environment: ApplicationEnvironment) -> StringTransformer:
        return _SelectStringTransformer(self._line_matcher.applier(environment))


class _SelectStringTransformer(WithCachedTreeStructureDescriptionBase, StringTransformer):
    """
    Keeps lines matched by a given :class:`LineMatcher`,
    and discards lines not matched.
    """
    NAME = names.SELECT_TRANSFORMER_NAME + ' ' + syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT.singular_name

    def __init__(self, line_matcher: LineMatcher):
        super().__init__()
        self._line_matcher = line_matcher

    @staticmethod
    def new_structure_tree(line_matcher: WithTreeStructureDescription) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            _SelectStringTransformer.NAME,
            None,
            (),
            (line_matcher.structure(),),
        )

    @property
    def name(self) -> str:
        return names.SELECT_TRANSFORMER_NAME

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._line_matcher)

    @property
    def line_matcher(self) -> LineMatcher:
        return self._line_matcher

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return (
            line
            for line, line_matcher_model in original_and_model_iter_from_file_line_iter(lines)
            if self._line_matcher.matches_w_trace(line_matcher_model).value
        )

    def __str__(self):
        return '{}({})'.format(type(self).__name__,
                               str(self._line_matcher))
