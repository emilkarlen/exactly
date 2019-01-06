from typing import Sequence, Optional

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.condition import comparison_structures
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as parse_expr
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.files_matcher.files_matchers import FilesMatcherResolverBase
from exactly_lib.test_case_utils.files_matcher.new_model import FilesMatcherModel
from exactly_lib.test_case_utils.files_matcher.structure import FilesMatcherResolver, \
    Environment
from exactly_lib.test_case_utils.validators import PreOrPostSdsValidatorFromValidatorViaExceptions, \
    SvhValidatorViaExceptionsFromPreAndPostSdsValidators
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.util import logic_types
from exactly_lib.util.logic_types import ExpectationType


def num_files_matcher(expectation_type: ExpectationType,
                      operator_and_r_operand: parse_expr.IntegerComparisonOperatorAndRightOperand
                      ) -> FilesMatcherResolver:
    validator = PreOrPostSdsValidatorFromValidatorViaExceptions(
        SvhValidatorViaExceptionsFromPreAndPostSdsValidators(
            pre_sds=comparison_structures.OperandValidator(operator_and_r_operand.right_operand))
    )
    return _NumFilesMatcher(expectation_type,
                            operator_and_r_operand,
                            validator)


class _NumFilesMatcher(FilesMatcherResolverBase):
    def __init__(self,
                 expectation_type: ExpectationType,
                 operator_and_r_operand: parse_expr.IntegerComparisonOperatorAndRightOperand,
                 validator: PreOrPostSdsValidator):
        self._operator_and_r_operand = operator_and_r_operand

        super().__init__(expectation_type,
                         validator)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._operator_and_r_operand.right_operand.references

    @property
    def negation(self) -> FilesMatcherResolver:
        return _NumFilesMatcher(logic_types.negation(self._expectation_type),
                                self._operator_and_r_operand,
                                self._validator
                                )

    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        comparison_handler = comparison_structures.ComparisonHandler(
            files_source.error_message_info.property_descriptor(config.NUM_FILES_PROPERTY_NAME),
            self._expectation_type,
            NumFilesResolver(files_source),
            self._operator_and_r_operand.operator,
            self._operator_and_r_operand.right_operand)

        env = environment.path_resolving_environment

        return comparison_handler.execute_and_report_as_err_msg_resolver(env)


class NumFilesResolver(comparison_structures.OperandResolver[int]):
    def __init__(self,
                 path_to_check: FilesMatcherModel):
        super().__init__(config.NUM_FILES_PROPERTY_NAME)
        self.path_to_check = path_to_check

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds) -> int:
        return len(list(self.path_to_check.files()))
