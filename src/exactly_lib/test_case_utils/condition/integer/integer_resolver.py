from typing import Sequence, Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils import svh_exception
from exactly_lib.test_case_utils.condition.comparison_structures import OperandResolver
from exactly_lib.test_case_utils.condition.integer.evaluate_integer import NotAnIntegerException, python_evaluate
from exactly_lib.test_case_utils.condition.integer.integer_value import CustomIntegerValidator, IntegerValue
from exactly_lib.test_case_utils.validators import SvhPreSdsValidatorViaExceptions
from exactly_lib.util import strings
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


class IntegerResolver(OperandResolver[int]):
    def __init__(self,
                 value_resolver: StringResolver,
                 custom_integer_validator: Optional[CustomIntegerValidator] = None):
        """
        :param value_resolver:
        :param custom_integer_validator: Function that takes the resolved value as only argument,
        and returns a str if validation fails, otherwise None
        """
        self._value_resolver = value_resolver
        self._custom_integer_validator = custom_integer_validator
        self._int_resolver = _IntResolver(value_resolver)
        self._validator = _ValidatorThatReportsViaExceptions(self._int_resolver, custom_integer_validator)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._value_resolver.references

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        self._validator.validate_pre_sds(environment)

    def resolve(self, symbols: SymbolTable) -> IntegerValue:
        return IntegerValue(self._value_resolver.resolve(symbols),
                            self._custom_integer_validator)


class _ValidatorThatReportsViaExceptions(SvhPreSdsValidatorViaExceptions):
    def __init__(self,
                 int_resolver: _IntResolver,
                 custom_integer_validator: Optional[CustomIntegerValidator]):
        self._int_resolver = int_resolver
        self._custom_integer_validator = custom_integer_validator

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):

        try:
            resolved_value = self._int_resolver.resolve(environment)
        except NotAnIntegerException as ex:
            msg = text_docs.single_pre_formatted_line_object(
                strings.FormatPositional(
                    'Argument must be an integer: `{}\'',
                    ex.value_string)
            )
            raise svh_exception.SvhValidationException(msg)

        self._validate_custom(resolved_value)

    def _validate_custom(self, resolved_value: int):
        if self._custom_integer_validator:
            err_msg = self._custom_integer_validator(resolved_value)
            if err_msg:
                raise svh_exception.SvhValidationException(err_msg)
