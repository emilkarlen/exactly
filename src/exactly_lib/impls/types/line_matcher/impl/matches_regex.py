from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.matcher import property_matcher
from exactly_lib.impls.types.matcher.impls import matches_regex, property_getters, property_matcher_describers
from exactly_lib.impls.types.matcher.property_getter import PropertyGetter
from exactly_lib.impls.types.regex import parse_regex
from exactly_lib.impls.types.regex.regex_ddv import RegexSdv
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.line_matcher import LineMatcherSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine
from exactly_lib.util.description_tree import renderers


def parse(token_parser: TokenParser) -> LineMatcherSdv:
    token_parser.require_has_valid_head_token(syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name)
    regex_sdv = parse_regex.parse_regex2(token_parser,
                                         must_be_on_same_line=True)

    return _sdv(regex_sdv)


def _sdv(regex: RegexSdv) -> LineMatcherSdv:
    return property_matcher.PropertyMatcherSdv(
        matches_regex.MatchesRegexSdv(regex, False),
        property_getters.sdv_of_constant_primitive(
            _PropertyGetter(),
        ),
        property_matcher_describers.IdenticalToMatcher(),
    )


class _PropertyGetter(PropertyGetter[LineMatcherLine, str]):
    def structure(self) -> StructureRenderer:
        return renderers.header_only('contents')

    def get_from(self, model: LineMatcherLine) -> str:
        return model[1]
