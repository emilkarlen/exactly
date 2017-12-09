from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions
from exactly_lib.instructions.utils.validators import SvhPreSdsValidatorViaExceptions
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.comparators import ComparisonOperator
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg.property_description import PropertyDescriptor
from exactly_lib.util.logic_types import ExpectationType


class OperandResolver:
    """Resolves an operand used in a comparision"""

    def __init__(self, property_name: str):
        self.property_name = property_name

    @property
    def references(self) -> list:
        return []

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        pass

    def resolve(self, environment: InstructionEnvironmentForPostSdsStep):
        """
        Reports errors by raising exceptions from `return_pfh_via_exceptions`
        
        :returns The value that can be used as one of the operands in a comparision.
        """
        raise NotImplementedError('abstract method')


class ErrorMessageConstructor:
    def error_message_lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        raise NotImplementedError('abstract method')


class EmptyErrorMessage(ErrorMessageConstructor):
    def error_message_lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        return []


class ComparisonHandler:
    """A comparison operator, resolvers for left and right operands, and an `ExpectationType`"""

    def __init__(self,
                 property_descriptor: PropertyDescriptor,
                 expectation_type: ExpectationType,
                 actual_value_lhs: OperandResolver,
                 operator: comparators.ComparisonOperator,
                 expected_value_rhs: OperandResolver,
                 description_of_actual: ErrorMessageConstructor = EmptyErrorMessage()):
        self.property_descriptor = property_descriptor
        self.expectation_type = expectation_type
        self.actual_value_lhs = actual_value_lhs
        self.integer_resolver = expected_value_rhs
        self.operator = operator
        self.description_of_actual = description_of_actual

    @property
    def references(self) -> list:
        return self.actual_value_lhs.references + self.integer_resolver.references

    @property
    def validator(self) -> SvhPreSdsValidatorViaExceptions:
        return Validator(self.actual_value_lhs, self.integer_resolver)

    def validate_pre_sds(self, environment: InstructionEnvironmentForPreSdsStep):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        self.validator.validate_pre_sds(environment.path_resolving_environment)

    def execute(self, environment: InstructionEnvironmentForPostSdsStep):
        """
        Reports failure by raising exceptions from `return_efh_via_exceptions`
        """
        lhs = self.actual_value_lhs.resolve(environment)
        rhs = self.integer_resolver.resolve(environment)
        executor = _ComparisonExecutor(
            self.expectation_type,
            lhs,
            rhs,
            self.operator,
            _FailureReporter(self.property_descriptor,
                             self.expectation_type,
                             lhs,
                             rhs,
                             self.operator,
                             environment,
                             self.description_of_actual)
        )
        executor.execute_and_return_pfh_via_exceptions()


class _FailureReporter:
    def __init__(self,
                 property_descriptor: PropertyDescriptor,
                 expectation_type: ExpectationType,
                 lhs_actual_property_value: int,
                 rhs: int,
                 operator: ComparisonOperator,
                 environment: InstructionEnvironmentForPostSdsStep,
                 description_of_actual: ErrorMessageConstructor):
        self.property_descriptor = property_descriptor
        self.expectation_type = expectation_type
        self.lhs_actual_property_value = lhs_actual_property_value
        self.rhs = rhs
        self.operator = operator
        self.environment = environment
        self.description_of_actual = description_of_actual

    def unexpected_value_message(self) -> str:
        return self.failure_info().error_message()

    def failure_info(self) -> diff_msg.DiffErrorInfo:
        expected_str = self.operator.name + ' ' + str(self.rhs)
        return diff_msg.DiffErrorInfo(
            self.property_descriptor.description(self.environment),
            self.expectation_type,
            expected_str,
            diff_msg.actual_with_single_line_value(str(self.lhs_actual_property_value))
        )


class _ComparisonExecutor:
    def __init__(self,
                 expectation_type: ExpectationType,
                 lhs_actual_property_value: int,
                 rhs: int,
                 operator: ComparisonOperator,
                 failure_reporter: _FailureReporter):
        self.expectation_type = expectation_type
        self.lhs_actual_property_value = lhs_actual_property_value
        self.rhs = rhs
        self.operator = operator
        self.failure_reporter = failure_reporter

    def execute_and_return_pfh_via_exceptions(self):
        comparison_fun = self.operator.operator_fun
        condition_is_satisfied = bool(comparison_fun(self.lhs_actual_property_value,
                                                     self.rhs))
        if condition_is_satisfied:
            if self.expectation_type is ExpectationType.NEGATIVE:
                self._raise_fail_exception()
        else:
            if self.expectation_type is ExpectationType.POSITIVE:
                self._raise_fail_exception()

    def _raise_fail_exception(self):
        err_msg = self.failure_reporter.unexpected_value_message()
        raise return_pfh_via_exceptions.PfhFailException(err_msg)


class Validator(SvhPreSdsValidatorViaExceptions):
    def __init__(self,
                 actual_value_lhs: OperandResolver,
                 expected_value_rhs: OperandResolver):
        self.actual_value_lhs = actual_value_lhs
        self.integer_resolver = expected_value_rhs

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        self.actual_value_lhs.validate_pre_sds(environment)
        self.integer_resolver.validate_pre_sds(environment)
