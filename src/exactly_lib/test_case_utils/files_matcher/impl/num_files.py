from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import property_getters, parse_integer_matcher, \
    property_matcher_describers
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcherSdv
from exactly_lib.util.description_tree import renderers

_NAME = ' '.join((config.NUM_FILES_CHECK_ARGUMENT,
                  syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name))


def parser() -> ParserFromTokens[FilesMatcherSdv]:
    return _PARSER


class _Parser(ParserFromTokens[FilesMatcherSdv]):
    INTEGER_MATCHER_PARSER = parse_integer_matcher.IntegerMatcherParser(
        parse_integer_matcher.validator_for_non_negative
    )

    def parse(self, token_parser: TokenParser) -> FilesMatcherSdv:
        matcher = self.INTEGER_MATCHER_PARSER.parse(token_parser)
        return property_matcher.PropertyMatcherSdv(
            matcher,
            property_getters.sdv_of_constant_primitive(_PropertyGetter()),
            property_matcher_describers.GetterWithMatcherAsChild()
        )


_PARSER = _Parser()


class _PropertyGetter(PropertyGetter[FilesMatcherModel, int], WithCachedTreeStructureDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only(_NAME)

    def get_from(self, model: FilesMatcherModel) -> int:
        ret_val = 0
        for _ in model.files():
            ret_val += 1

        return ret_val
