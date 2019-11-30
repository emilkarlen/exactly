from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import property_getters, parse_integer_matcher, \
    property_matcher_describers
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter, PropertyGetterSdv
from exactly_lib.test_case_utils.string_matcher import delegated_matcher, matcher_options
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.logic_types import ExpectationType

_NAME = ' '.join((matcher_options.NUM_LINES_ARGUMENT,
                  syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.singular_name))


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherSdv:
    matcher = parse_integer_matcher.parse(
        token_parser,
        expectation_type,
        parse_integer_matcher.validator_for_non_negative,
    )
    return delegated_matcher.StringMatcherSdvDelegatedToMatcher(
        property_matcher.PropertyMatcherSdv(
            matcher,
            _operand_from_model_sdv(),
            property_matcher_describers.NamedWithMatcherAsChild(_NAME)
        ),
    )


class _PropertyGetter(PropertyGetter[FileToCheck, int]):
    def get_from(self, model: FileToCheck) -> int:
        ret_val = 0
        with model.lines() as lines:
            for _ in lines:
                ret_val += 1
        return ret_val


def _operand_from_model_sdv() -> PropertyGetterSdv[FileToCheck, int]:
    return property_getters.PropertyGetterSdvConstant(
        property_getters.PropertyGetterDdvConstant(
            _PropertyGetter(),
        )
    )
