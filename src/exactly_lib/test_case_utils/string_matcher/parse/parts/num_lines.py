from typing import Optional, Sequence, Set

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils import return_pfh_via_exceptions, return_svh_via_exceptions
from exactly_lib.test_case_utils.condition import comparison_structures
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as parse_cmp_op
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import \
    IntegerComparisonOperatorAndRightOperand
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import validator_for_non_negative
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.test_case_utils.string_matcher.resolvers import StringMatcherResolverFromParts
from exactly_lib.test_case_utils.validators import SvhPreSdsValidatorViaExceptions
from exactly_lib.type_system.error_message import ErrorMessageResolver, ConstantErrorMessageResolver
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcher
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherResolver:
    cmp_op_and_rhs = parse_cmp_op.parse_integer_comparison_operator_and_rhs(token_parser,
                                                                            validator_for_non_negative)
    token_parser.report_superfluous_arguments_if_not_at_eol()
    token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
    return value_resolver(expectation_type,
                          cmp_op_and_rhs)


def value_resolver(expectation_type: ExpectationType,
                   cmp_op_and_rhs: IntegerComparisonOperatorAndRightOperand,
                   ) -> StringMatcherResolver:
    def get_resolving_dependencies(symbols: SymbolTable) -> Set[DirectoryStructurePartition]:
        return cmp_op_and_rhs.right_operand.resolve(symbols).resolving_dependencies()

    def get_matcher(environment: PathResolvingEnvironmentPreOrPostSds) -> StringMatcher:
        return NumLinesStringMatcher(
            cmp_op_and_rhs,
            expectation_type,
            environment,
        )

    return StringMatcherResolverFromParts(
        cmp_op_and_rhs.right_operand.references,
        _PreOrPostSdsValidator(cmp_op_and_rhs.right_operand.validator),
        get_resolving_dependencies,
        get_matcher,
    )


class NumLinesStringMatcher(StringMatcher):
    @property
    def option_description(self) -> str:
        return diff_msg.negation_str(self._expectation_type) + matcher_options.NUM_LINES_DESCRIPTION

    def __init__(self,
                 cmp_op_and_rhs: IntegerComparisonOperatorAndRightOperand,
                 expectation_type: ExpectationType,
                 environment: PathResolvingEnvironmentPreOrPostSds,
                 ):
        self._cmp_op_and_rhs = cmp_op_and_rhs
        self._environment = environment
        self._expectation_type = expectation_type

    def matches(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        comparison_handler = comparison_structures.ComparisonHandler(
            model.describer.construct_for_contents_attribute(
                matcher_options.NUM_LINES_DESCRIPTION),
            self._expectation_type,
            NumLinesResolver(model),
            self._cmp_op_and_rhs.operator,
            self._cmp_op_and_rhs.right_operand)

        try:
            comparison_handler.execute(self._environment)
        except return_pfh_via_exceptions.PfhException as ex:
            return ConstantErrorMessageResolver(ex.err_msg)


class NumLinesResolver(comparison_structures.OperandResolver[int]):
    def __init__(self,
                 file_to_check: FileToCheck):
        super().__init__(matcher_options.NUM_LINES_DESCRIPTION)
        self.file_to_check = file_to_check

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds) -> int:
        ret_val = 0
        with self.file_to_check.lines() as lines:
            for line in lines:
                ret_val += 1
        return ret_val


class _PreOrPostSdsValidator(PreOrPostSdsValidator):
    def __init__(self, adapted: SvhPreSdsValidatorViaExceptions):
        self._adapted = adapted

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[str]:
        try:
            self._adapted.validate_pre_sds(environment)
        except return_svh_via_exceptions.SvhException as ex:
            return ex.err_msg

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[str]:
        return None
