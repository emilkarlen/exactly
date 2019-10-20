from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic, Set, Optional, Callable

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils import pfh_exception
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.comparators import ComparisonOperator
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.validators import SvhPreSdsValidatorViaExceptions
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.err_msg.prop_descr import PropertyDescriptor
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable

A = TypeVar('A')
T = TypeVar('T')


class _ErrorMessageResolver(Generic[T], ErrorMessageResolver):
    def __init__(self,
                 property_descriptor: PropertyDescriptor,
                 expectation_type: ExpectationType,
                 lhs_actual_property_value: T,
                 rhs: T,
                 operator: ComparisonOperator):
        self.property_descriptor = property_descriptor
        self.expectation_type = expectation_type
        self.lhs_actual_property_value = lhs_actual_property_value
        self.rhs = rhs
        self.operator = operator

    def resolve(self) -> str:
        return self.failure_info().error_message()

    def failure_info(self) -> diff_msg.DiffErrorInfo:
        expected_str = self.operator.name + ' ' + str(self.rhs)
        return diff_msg.DiffErrorInfo(
            self.property_descriptor.description(),
            self.expectation_type,
            expected_str,
            diff_msg.actual_with_single_line_value(str(self.lhs_actual_property_value))
        )


class _FailureReporter(Generic[T]):
    def __init__(self,
                 err_msg_resolver: _ErrorMessageResolver[T],
                 ):
        self.err_msg_resolver = err_msg_resolver

    def unexpected_value_message(self) -> str:
        return self.err_msg_resolver.resolve()

    def failure_info(self) -> diff_msg.DiffErrorInfo:
        return self.err_msg_resolver.failure_info()


class ComparisonExecutor(Generic[T]):
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

    def execute_and_return_failure_via_err_msg_resolver(self) -> Optional[ErrorMessageResolver]:
        return self._execute(self._get_err_msg_resolver)

    def execute_and_return_pfh_via_exceptions(self):
        self._execute(self._raise_fail_exception)

    def _execute(self, failure_reporter: Callable[[], ErrorMessageResolver]) -> Optional[ErrorMessageResolver]:
        comparison_fun = self.operator.operator_fun
        condition_is_satisfied = bool(comparison_fun(self.lhs_actual_property_value,
                                                     self.rhs))
        if condition_is_satisfied:
            if self.expectation_type is ExpectationType.NEGATIVE:
                return failure_reporter()
        else:
            if self.expectation_type is ExpectationType.POSITIVE:
                return failure_reporter()

    def _raise_fail_exception(self):
        err_msg = self.failure_reporter.unexpected_value_message()
        raise pfh_exception.PfhFailException(text_docs.single_pre_formatted_line_object(err_msg))

    def _get_err_msg_resolver(self) -> ErrorMessageResolver:
        return self.failure_reporter.err_msg_resolver


class OperandValue(ABC, Generic[T], MultiDirDependentValue[T]):
    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    def value_when_no_dir_dependencies(self) -> T:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise ValueError(str(type(self)) + ' do not support this short cut.')

    @abstractmethod
    def value_of_any_dependency(self, tcds: HomeAndSds) -> T:
        """Gives the value, regardless of actual dependency."""
        pass


class OperandResolver(Generic[T], ABC):
    """Resolves an operand used in a comparision"""

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> OperandValue[T]:
        pass


class ComparisonHandlerValue(Generic[T]):
    """A comparison operator, resolvers for left and right operands, and an `ExpectationType`"""

    def __init__(self,
                 property_descriptor: PropertyDescriptor,
                 expectation_type: ExpectationType,
                 actual_value_lhs: OperandValue[T],
                 operator: comparators.ComparisonOperator,
                 expected_value_rhs: OperandValue[T]):
        self.property_descriptor = property_descriptor
        self.expectation_type = expectation_type
        self.actual_value_lhs = actual_value_lhs
        self.expected_value_rhs = expected_value_rhs
        self.operator = operator

    def value_of_any_dependency(self, tcds: HomeAndSds) -> ComparisonExecutor:
        lhs = self.actual_value_lhs.value_of_any_dependency(tcds)
        rhs = self.expected_value_rhs.value_of_any_dependency(tcds)
        return ComparisonExecutor(
            self.expectation_type,
            lhs,
            rhs,
            self.operator,
            _FailureReporter(_ErrorMessageResolver(self.property_descriptor,
                                                   self.expectation_type,
                                                   lhs,
                                                   rhs,
                                                   self.operator),
                             )
        )


class ComparisonHandlerResolver(Generic[T]):
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
        self.expected_value_rhs = expected_value_rhs
        self.operator = operator

    @property
    def references(self) -> Sequence[SymbolReference]:
        return list(self.actual_value_lhs.references) + list(self.expected_value_rhs.references)

    @property
    def validator(self) -> SvhPreSdsValidatorViaExceptions:
        return Validator(self.actual_value_lhs, self.expected_value_rhs)

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        self.validator.validate_pre_sds(environment)

    def resolve(self, symbols: SymbolTable) -> ComparisonHandlerValue:
        return ComparisonHandlerValue(
            self.property_descriptor,
            self.expectation_type,
            self.actual_value_lhs.resolve(symbols),
            self.operator,
            self.expected_value_rhs.resolve(symbols),
        )


class Validator(SvhPreSdsValidatorViaExceptions):
    def __init__(self,
                 actual_value_lhs: OperandResolver,
                 expected_value_rhs: OperandResolver):
        self.actual_value_lhs = actual_value_lhs
        self.expected_value_rhs = expected_value_rhs

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        self.actual_value_lhs.validate_pre_sds(environment)
        self.expected_value_rhs.validate_pre_sds(environment)


class OperandValidator(SvhPreSdsValidatorViaExceptions):
    def __init__(self, operand: OperandResolver):
        self.operand = operand

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        self.operand.validate_pre_sds(environment)
