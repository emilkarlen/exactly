from typing import Sequence, Optional, Callable

from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils import return_svh_via_exceptions
from exactly_lib.test_case_utils.condition.comparison_structures import OperandResolver
from exactly_lib.test_case_utils.condition.integer.evaluate_integer import NotAnIntegerException, python_evaluate
from exactly_lib.test_case_utils.validators import SvhPreSdsValidatorViaExceptions


class _IntResolver:
    def __init__(self, value_resolver: StringResolver):
        self.value_resolver = value_resolver

    def resolve(self, environment: PathResolvingEnvironmentPreSds) -> int:
        """
        :raises NotAnIntegerException
        """
        value_string = self.value_resolver.resolve(environment.symbols).value_when_no_dir_dependencies()
        return python_evaluate(value_string)


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
        self.value_resolver = value_resolver
        self.custom_integer_validator = custom_integer_validator
        self._int_resolver = _IntResolver(value_resolver)
        self._validator = _Validator(self._int_resolver, custom_integer_validator)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.value_resolver.references

    @property
    def validator(self) -> SvhPreSdsValidatorViaExceptions:
        return self._validator

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        self._validator.validate_pre_sds(environment)

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds) -> int:
        try:
            return self._int_resolver.resolve(environment)
        except NotAnIntegerException as ex:
            msg = ('Argument is not an integer,'
                   ' even though this should have been checked by the validation: `{}\''.format(ex.value_string))
            raise return_svh_via_exceptions.SvhHardErrorException(msg)
