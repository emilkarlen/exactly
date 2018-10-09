from typing import Sequence, TypeVar, Generic

from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions
from exactly_lib.instructions.utils.validators import SvhPreSdsValidatorViaExceptions
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.comparators import ComparisonOperator
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, PropertyDescriptor
from exactly_lib.util.logic_types import ExpectationType

T = TypeVar('T')


class OperandResolver(Generic[T]):
    """Resolves an operand used in a comparision"""

    def __init__(self, property_name: str):
        self.property_name = property_name

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        pass

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> T:
        """
        Reports errors by raising exceptions from `return_pfh_via_exceptions`
        
        :returns The value that can be used as one of the operands in a comparision.
        """
        raise NotImplementedError('abstract method')


class ComparisonHandler(Generic[T]):
    """A comparison operator, resolvers for left and right operands, and an `ExpectationType`"""

    def __init__(self,
                 property_descriptor: PropertyDescriptor,
                 expectation_type: ExpectationType,
                 actual_value_lhs: OperandResolver[T],
                 operator: comparators.ComparisonOperator,
                 expected_value_rhs: OperandResolver[T]):
        self.property_descriptor = property_descriptor
        self.expectation_type = expectation_type
        self.actual_value_lhs = actual_value_lhs
        self.integer_resolver = expected_value_rhs
        self.operator = operator

    @property
    def references(self) -> Sequence[SymbolReference]:
        return list(self.actual_value_lhs.references) + list(self.integer_resolver.references)

    @property
    def validator(self) -> SvhPreSdsValidatorViaExceptions:
        return Validator(self.actual_value_lhs, self.integer_resolver)

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        self.validator.validate_pre_sds(environment)

    def execute(self, environment: PathResolvingEnvironmentPreOrPostSds):
        """
        Reports failure by raising exceptions from `return_efh_via_exceptions`
        """
        err_msg_env = ErrorMessageResolvingEnvironment(environment.home_and_sds,
                                                       environment.symbols)
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
                             err_msg_env)
        )
        executor.execute_and_return_pfh_via_exceptions()


class _FailureReporter(Generic[T]):
    def __init__(self,
                 property_descriptor: PropertyDescriptor,
                 expectation_type: ExpectationType,
                 lhs_actual_property_value: T,
                 rhs: T,
                 operator: ComparisonOperator,
                 environment: ErrorMessageResolvingEnvironment):
        self.property_descriptor = property_descriptor
        self.expectation_type = expectation_type
        self.lhs_actual_property_value = lhs_actual_property_value
        self.rhs = rhs
        self.operator = operator
        self.environment = environment

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


class _ComparisonExecutor(Generic[T]):
    def __init__(self,
                 expectation_type: ExpectationType,
                 lhs_actual_property_value: T,
                 rhs: T,
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
