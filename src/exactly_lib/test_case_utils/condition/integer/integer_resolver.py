from typing import Sequence, Optional, Callable, Set

from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPreOrPostSds, PathResolvingEnvironmentPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils import return_svh_via_exceptions
from exactly_lib.test_case_utils.condition.comparison_structures import OperandResolver, OperandValue
from exactly_lib.test_case_utils.condition.integer.evaluate_integer import NotAnIntegerException, python_evaluate
from exactly_lib.test_case_utils.validators import SvhPreSdsValidatorViaExceptions
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.util.symbol_table import SymbolTable


class _IntResolver:
    def __init__(self, value_resolver: StringResolver):
        self.value_resolver = value_resolver

    def resolve(self, environment: PathResolvingEnvironmentPreSds) -> int:
        """
        :raises NotAnIntegerException
        """
        value_string = self.value_resolver.resolve(environment.symbols).value_when_no_dir_dependencies()
        return python_evaluate(value_string)


class _PrimitiveValueComputer:
    """Computes the primitive value"""

    def __init__(self, int_expression: StringValue):
        self._int_expression = int_expression
        self._primitive_value = None

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._int_expression.resolving_dependencies()

    def value_when_no_dir_dependencies(self) -> int:
        if self._primitive_value is not None:
            return self._primitive_value
        else:
            return self._get_primitive_value(self._int_expression.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, tcds: HomeAndSds) -> int:
        if self._primitive_value is not None:
            return self._primitive_value
        else:
            return self._get_primitive_value(self._int_expression.value_of_any_dependency(tcds))

    def _get_primitive_value(self, int_expr: str) -> int:
        try:
            self._primitive_value = python_evaluate(int_expr)
        except NotAnIntegerException as ex:
            msg = 'Not an integer expression: `{}\''.format(ex.value_string)
            raise NotAnIntegerException(msg)

        return self._primitive_value


class IntegerValue(OperandValue[int]):
    def __init__(self,
                 int_expression: StringValue,
                 custom_integer_validator: Optional[Callable[[int], Optional[str]]] = None):
        self._primitive_value_computer = _PrimitiveValueComputer(int_expression)
        self._validator = _IntegerValueValidator(self._primitive_value_computer,
                                                 custom_integer_validator)

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._primitive_value_computer.resolving_dependencies()

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_when_no_dir_dependencies(self) -> int:
        return self._primitive_value_computer.value_when_no_dir_dependencies()

    def value_of_any_dependency(self, tcds: HomeAndSds) -> int:
        return self._primitive_value_computer.value_of_any_dependency(tcds)


class IntegerResolver(OperandResolver[int]):
    def __init__(self,
                 property_name: str,
                 value_resolver: StringResolver,
                 custom_integer_validator: Optional[Callable[[int], Optional[str]]] = None):
        """
        :param property_name:
        :param value_resolver:
        :param custom_integer_validator: Function that takes the resolved value as only argument,
        and returns a str if validation fails, otherwise None
        """
        super().__init__(property_name)
        self._value_resolver = value_resolver
        self._custom_integer_validator = custom_integer_validator
        self._int_resolver = _IntResolver(value_resolver)
        self._validator = _Validator(self._int_resolver, custom_integer_validator)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._value_resolver.references

    @property
    def validator(self) -> SvhPreSdsValidatorViaExceptions:
        return self._validator

    @property
    def pre_or_post_sds_validator(self) -> PreOrPostSdsValidator:
        """
        Gives a validator that always will do validation pre sds.
        """
        return _PreOrPostSdsValidator(self._validator)

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        self._validator.validate_pre_sds(environment)

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds) -> int:
        try:
            return self._int_resolver.resolve(environment)
        except NotAnIntegerException as ex:
            msg = ('Argument is not an integer,'
                   ' even though this should have been checked by the validation: `{}\''.format(ex.value_string))
            raise return_svh_via_exceptions.SvhHardErrorException(msg)

    def resolve(self, symbols: SymbolTable) -> IntegerValue:
        return IntegerValue(self._value_resolver.resolve(symbols),
                            self._custom_integer_validator)


class _Validator(SvhPreSdsValidatorViaExceptions):
    def __init__(self,
                 int_resolver: _IntResolver,
                 custom_integer_validator: Optional[Callable[[int], Optional[str]]]):
        self._int_resolver = int_resolver
        self._custom_integer_validator = custom_integer_validator

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):

        try:
            resolved_value = self._int_resolver.resolve(environment)
        except NotAnIntegerException as ex:
            msg = 'Argument must be an integer: `{}\''.format(ex.value_string)
            raise return_svh_via_exceptions.SvhValidationException(msg)

        self._validate_custom(resolved_value)

    def _validate_custom(self, resolved_value: int):
        if self._custom_integer_validator:
            err_msg = self._custom_integer_validator(resolved_value)
            if err_msg:
                raise return_svh_via_exceptions.SvhValidationException(err_msg)


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


class _IntegerValueValidator(PreOrPostSdsValueValidator):
    def __init__(self,
                 value_computer: _PrimitiveValueComputer,
                 custom_validator: Optional[Callable[[int], Optional[str]]]):
        self._value_computer = value_computer
        self._custom_validator = (custom_validator
                                  if custom_validator is not None
                                  else
                                  lambda x: None)
        self._has_dir_dependencies = bool(self._value_computer.resolving_dependencies())

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[str]:
        if not self._has_dir_dependencies:
            try:
                x = self._value_computer.value_when_no_dir_dependencies()
                return self._custom_validator(x)
            except NotAnIntegerException as ex:
                return ex.value_string

        return None

    def validate_post_sds_if_applicable(self, tcds: HomeAndSds) -> Optional[str]:
        if self._has_dir_dependencies:
            try:
                x = self._value_computer.value_of_any_dependency(tcds)
                return self._custom_validator(x)
            except NotAnIntegerException as ex:
                return ex.value_string

        return None
