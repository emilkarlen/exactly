from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import property_getters, parse_integer_matcher, \
    property_matcher_describers, combinator_sdvs
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcherSdv
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.logic_types import ExpectationType

_NAME = ' '.join((config.NUM_FILES_CHECK_ARGUMENT,
                  syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name))


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> FilesMatcherSdv:
    matcher = parse_integer_matcher.parse(
        token_parser,
        parse_integer_matcher.validator_for_non_negative,
    )
    matcher = combinator_sdvs.optionally_negated(matcher, expectation_type)
    return property_matcher.PropertyMatcherSdv(
        matcher,
        property_getters.sdv_of_constant_primitive(_PropertyGetter()),
        property_matcher_describers.GetterWithMatcherAsChild()
    )


class _PropertyGetter(PropertyGetter[FilesMatcherModel, int], WithCachedTreeStructureDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only(_NAME)

    def get_from(self, model: FilesMatcherModel) -> int:
        ret_val = 0
        for _ in model.files():
            ret_val += 1

        return ret_val
