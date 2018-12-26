from typing import Optional, Sequence

from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileContentsAssertionPart
from exactly_lib.instructions.utils import return_svh_via_exceptions
from exactly_lib.instructions.utils.validators import SvhPreSdsValidatorViaExceptions
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.condition import comparison_structures
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as parse_cmp_op
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import \
    IntegerComparisonOperatorAndRightOperand
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import validator_for_non_negative
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.logic_types import ExpectationType


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> FileContentsAssertionPart:
    cmp_op_and_rhs = parse_cmp_op.parse_integer_comparison_operator_and_rhs(token_parser,
                                                                            validator_for_non_negative)
    token_parser.report_superfluous_arguments_if_not_at_eol()
    token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
    return _assertion_part_for_num_lines(expectation_type,
                                         cmp_op_and_rhs)


def _assertion_part_for_num_lines(expectation_type: ExpectationType,
                                  cmp_op_and_rhs: IntegerComparisonOperatorAndRightOperand,
                                  ) -> FileContentsAssertionPart:
    return NumLinesContentsAssertionPart(expectation_type, cmp_op_and_rhs)


class NumLinesContentsAssertionPart(FileContentsAssertionPart):
    def __init__(self,
                 expectation_type: ExpectationType,
                 cmp_op_and_rhs: IntegerComparisonOperatorAndRightOperand):
        super().__init__(_PreOrPostSdsValidator(cmp_op_and_rhs.right_operand.validator))
        self.expectation_type = expectation_type
        self.cmp_op_and_rhs = cmp_op_and_rhs

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              file_to_check: FileToCheck) -> FileToCheck:
        comparison_handler = comparison_structures.ComparisonHandler(
            file_to_check.describer.construct_for_contents_attribute(
                instruction_options.NUM_LINES_DESCRIPTION),
            self.expectation_type,
            NumLinesResolver(file_to_check),
            self.cmp_op_and_rhs.operator,
            self.cmp_op_and_rhs.right_operand)

        comparison_handler.execute(environment.path_resolving_environment_pre_or_post_sds)
        return file_to_check

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.cmp_op_and_rhs.right_operand.references


class NumLinesResolver(comparison_structures.OperandResolver[int]):
    def __init__(self,
                 file_to_check: FileToCheck):
        super().__init__(instruction_options.NUM_LINES_DESCRIPTION)
        self.file_to_check = file_to_check

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> int:
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
