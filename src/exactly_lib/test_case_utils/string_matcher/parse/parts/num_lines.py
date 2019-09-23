from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as parse_cmp_op
from exactly_lib.test_case_utils.matcher import applier
from exactly_lib.test_case_utils.matcher.element_getter import ElementGetter, ElementGetterResolver
from exactly_lib.test_case_utils.matcher.impls import element_getters, parse_integer_matcher
from exactly_lib.test_case_utils.matcher.impls.err_msg import ErrorMessageResolverForFailure
from exactly_lib.test_case_utils.matcher.matcher import Failure
from exactly_lib.test_case_utils.string_matcher import matcher_applier, matcher_options
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
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
        matcher_options.NUM_LINES_ARGUMENT,
        applier.MatcherApplierResolver(
            matcher,
            _operand_from_model_resolver(),
        ),
        _mk_error_message,
    )


class _ElementGetter(ElementGetter[FileToCheck, int]):
    def get_from(self, model: FileToCheck) -> int:
        ret_val = 0
        with model.lines() as lines:
            for _ in lines:
                ret_val += 1
        return ret_val


def _operand_from_model_resolver() -> ElementGetterResolver[FileToCheck, int]:
    return element_getters.ElementGetterResolverConstant(
        element_getters.ElementGetterValueConstant(
            _ElementGetter(),
        )
    )


def _mk_error_message(model: FileToCheck, failure: Failure[int]) -> ErrorMessageResolver:
    return ErrorMessageResolverForFailure(
        model.describer.construct_for_contents_attribute(
            matcher_options.NUM_LINES_DESCRIPTION),
        failure,
    )
