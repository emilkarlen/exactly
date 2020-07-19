from typing import Sequence, Iterator

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.line_matcher.model_construction import original_and_model_iter_from_file_line_iter
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.test_case_utils.string_transformer.impl.transformed_string_models import \
    StringTransformerFromLinesTransformer
from exactly_lib.type_system.description.tree_structured import StructureRenderer, WithTreeStructureDescription
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherAdv, LineMatcherDdv, \
    LineMatcherSdv
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv, StringTransformer, \
    StringTransformerAdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parse_filter(parser: TokenParser) -> StringTransformerSdv:
    line_matcher = parse_line_matcher.parse_line_matcher_from_token_parser(parser)
    return _StringTransformerSelectSdv(line_matcher)


class _StringTransformerSelectSdv(StringTransformerSdv):
    def __init__(self, line_matcher_sdv: LineMatcherSdv):
        self.line_matcher_sdv = line_matcher_sdv

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.line_matcher_sdv.references

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return _SelectStringTransformerDdv(self.line_matcher_sdv.resolve(symbols))


class _SelectStringTransformerDdv(StringTransformerDdv):
    """
    Keeps lines matched by a given Line Matcher
    and discards lines not matched.
    """

    def __init__(self, line_matcher: LineMatcherDdv):
        self._line_matcher = line_matcher

    def structure(self) -> StructureRenderer:
        return _SelectStringTransformer.new_structure_tree(self._line_matcher)

    @property
    def validator(self) -> DdvValidator:
        return self._line_matcher.validator

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerAdv:
        return _SelectStringTransformerAdv(self._line_matcher.value_of_any_dependency(tcds))


class _SelectStringTransformerAdv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self, line_matcher: LineMatcherAdv):
        self._line_matcher = line_matcher

    def primitive(self, environment: ApplicationEnvironment) -> StringTransformer:
        return _SelectStringTransformer(self._line_matcher.primitive(environment))


class _SelectStringTransformer(WithCachedTreeStructureDescriptionBase, StringTransformerFromLinesTransformer):
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

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        return (
            line
            for line, line_matcher_model in original_and_model_iter_from_file_line_iter(lines)
            if self._line_matcher.matches_w_trace(line_matcher_model).value
        )

    def __str__(self):
        return '{}({})'.format(type(self).__name__,
                               str(self._line_matcher))


class SyntaxDescription(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.MANDATORY,
                     instruction_arguments.LINE_MATCHER),
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TEXT_PARSER.fnap(_SELECT_TRANSFORMER_SED_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [types.LINE_MATCHER_TYPE_INFO.cross_reference_target]


_TEXT_PARSER = TextParser({
    '_LINE_MATCHER_': syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT.singular_name,
})

_SELECT_TRANSFORMER_SED_DESCRIPTION = """\
Keeps lines matched by {_LINE_MATCHER_},
and discards lines not matched.
"""
