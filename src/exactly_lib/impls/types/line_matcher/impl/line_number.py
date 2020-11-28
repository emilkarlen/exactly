from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.impls.types.integer_matcher import parse_integer_matcher
from exactly_lib.impls.types.interval import matcher_interval
from exactly_lib.impls.types.matcher import property_matcher
from exactly_lib.impls.types.matcher.impls import property_getters, \
    property_matcher_describers
from exactly_lib.impls.types.matcher.property_getter import PropertyGetterSdv
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.line_matcher import LineMatcherSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.integer_matcher import IntegerMatcher
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.interval.w_inversion import intervals
from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion

_NAME = ' '.join((line_matcher.LINE_NUMBER_MATCHER_NAME,
                  syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name))


def parse_line_number(parser: TokenParser) -> LineMatcherSdv:
    integer_matcher = _MATCHER_PARSER.parse_from_token_parser(parser)
    return property_matcher.PropertyMatcherSdv(
        integer_matcher,
        _operand_from_model_sdv(),
        property_matcher_describers.GetterWithMatcherAsChild(),
        _get_int_interval_of_int_matcher,
    )


_MATCHER_PARSER = parse_integer_matcher.parsers().simple


def _operand_from_model_sdv() -> PropertyGetterSdv[LineMatcherLine, int]:
    return property_getters.PropertyGetterSdvConstant(
        property_getters.PropertyGetterDdvConstant(
            _PropertyGetter(),
        )
    )


class _PropertyGetter(property_getters.PropertyGetter[LineMatcherLine, int], WithCachedNodeDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only(_NAME)

    def get_from(self, model: LineMatcherLine) -> int:
        return model[0]


def _get_int_interval_of_int_matcher(matcher: IntegerMatcher) -> IntIntervalWInversion:
    return matcher_interval.interval_of__w_inversion(matcher,
                                                     _INTERVAL_OF_UNKNOWN_INT_MATCHER,
                                                     matcher_interval.no_adaption)


_INTERVAL_OF_UNKNOWN_INT_MATCHER = intervals.unlimited_with_unlimited_inversion()
