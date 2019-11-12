from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic, Set

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.condition.comparators import ComparisonOperator
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.err_msg.prop_descr import PropertyDescriptor
from exactly_lib.util.description_tree.renderer import DetailsRenderer
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


class OperandDdv(Generic[T], MultiDependenciesDdv[T], ABC):
    @abstractmethod
    def describer(self) -> DetailsRenderer:
        pass

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
    def resolve(self, symbols: SymbolTable) -> OperandDdv[T]:
        pass
