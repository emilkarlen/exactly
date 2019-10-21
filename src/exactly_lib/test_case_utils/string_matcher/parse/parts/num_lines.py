from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as parse_cmp_op
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import element_getters, parse_integer_matcher
from exactly_lib.test_case_utils.matcher.impls.err_msg import ErrorMessageResolverForFailure
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter, PropertyGetterResolver
from exactly_lib.test_case_utils.string_matcher import matcher_applier, matcher_options
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import Failure
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.logic_types import ExpectationType


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherResolver:
    matcher = parse_integer_matcher.parse(
        token_parser,
        expectation_type,
        parse_cmp_op.validator_for_non_negative,
    )
    return matcher_applier.MaStringMatcherResolver(
        property_matcher.PropertyMatcherResolver(
            matcher,
            _operand_from_model_resolver(),
        ),
        _mk_error_message,
    )


class _PropertyGetter(PropertyGetter[FileToCheck, int]):
    NAME = ' '.join((matcher_options.NUM_LINES_ARGUMENT,
                     syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.singular_name))

    @property
    def name(self) -> str:
        return self.NAME

    def get_from(self, model: FileToCheck) -> int:
        ret_val = 0
        with model.lines() as lines:
            for _ in lines:
                ret_val += 1
        return ret_val


def _operand_from_model_resolver() -> PropertyGetterResolver[FileToCheck, int]:
    return element_getters.PropertyGetterResolverConstant(
        element_getters.PropertyGetterValueConstant(
            _PropertyGetter(),
        )
    )


def _mk_error_message(model: FileToCheck, failure: Failure[int]) -> ErrorMessageResolver:
    return ErrorMessageResolverForFailure(
        model.describer.construct_for_contents_attribute(
            matcher_options.NUM_LINES_DESCRIPTION),
        failure,
    )
