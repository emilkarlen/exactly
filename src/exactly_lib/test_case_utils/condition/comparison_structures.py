from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic, Set, Iterable

from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions
from exactly_lib.instructions.utils.validators import SvhPreSdsValidatorViaExceptions
from exactly_lib.symbol.lookups import lookup_container
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.comparators import ComparisonOperator
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.type_system import utils
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, PropertyDescriptor
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


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

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds) -> T:
        """
        Reports errors by raising exceptions from `return_pfh_via_exceptions`
        
        :returns The value that can be used as one of the operands in a comparision.
        """
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> OperandValue[T]:
        return OperandValueFromOperandResolver(self, symbols)


class OperandValueFromOperandResolver(Generic[T], OperandValue[T]):
    def __init__(self,
                 operand_resolver: OperandResolver[T],
                 symbols: SymbolTable):
        self._operand_resolver = operand_resolver
        self._symbols = symbols

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return resolving_dependencies_from_references(self._operand_resolver.references,
                                                      self._symbols)

    def value_of_any_dependency(self, tcds: HomeAndSds) -> T:
        environment = PathResolvingEnvironmentPreOrPostSds(tcds, self._symbols)
        return self._operand_resolver.resolve_value_of_any_dependency(environment)


def resolving_dependencies_from_references(references: Iterable[SymbolReference],
                                           symbols: SymbolTable) -> Set[DirectoryStructurePartition]:
    values = [
        lookup_container(symbols, reference.name).resolver.resolve(symbols)
        for reference in references
    ]
    return utils.resolving_dependencies_from_sequence(values)


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
        lhs = self.actual_value_lhs.resolve_value_of_any_dependency(environment)
        rhs = self.integer_resolver.resolve_value_of_any_dependency(environment)
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
