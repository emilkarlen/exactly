from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import matches_regex, property_getters, property_matcher_describers
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_ddv import RegexSdv
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileMatcherSdv
from exactly_lib.util.description_tree import renderers

_PROPERTY_NAME = 'base-name'


def parse(token_parser: TokenParser) -> FileMatcherSdv:
    token_parser.require_has_valid_head_token(syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name)
    source_type, regex_sdv = parse_regex.parse_regex2(token_parser,
                                                      must_be_on_same_line=True)

    return _sdv(regex_sdv)


def _sdv(regex: RegexSdv) -> FileMatcherSdv:
    return property_matcher.PropertyMatcherSdv(
        matches_regex.MatchesRegexSdv(regex, False),
        property_getters.sdv_of_constant_primitive(
            _BaseNamePropertyGetter(),
        ),
        property_matcher_describers.GetterWithMatcherAsDetail(),
    )


class _BaseNamePropertyGetter(PropertyGetter[FileMatcherModel, str], WithCachedTreeStructureDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only(_PROPERTY_NAME)

    def get_from(self, model: FileMatcherModel) -> str:
        return model.path.primitive.name
