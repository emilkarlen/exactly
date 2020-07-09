from typing import Sequence, Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds
from exactly_lib.symbol.sdv_structure import SymbolReference, ObjectWithSymbolReferences
from exactly_lib.test_case_utils import svh_exception
from exactly_lib.test_case_utils.condition.comparison_structures import OperandSdv
from exactly_lib.test_case_utils.condition.integer.evaluate_integer import NotAnIntegerException, python_evaluate
from exactly_lib.test_case_utils.condition.integer.integer_ddv import CustomIntegerValidator, IntegerDdv
from exactly_lib.test_case_utils.validators import SvhPreSdsValidatorViaExceptions
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.symbol_table import SymbolTable


class _IntResolver:
    def __init__(self, value_sdv: StringSdv):
        self.value_sdv = value_sdv

    def resolve(self, environment: PathResolvingEnvironmentPreSds) -> int:
        """
        :raises NotAnIntegerException
        """
        value_string = self.value_sdv.resolve(environment.symbols).value_when_no_dir_dependencies()
        return python_evaluate(value_string)


class IntegerSdv(OperandSdv[int], ObjectWithSymbolReferences):
    def __init__(self,
                 value_sdv: StringSdv,
                 custom_integer_validator: Optional[CustomIntegerValidator] = None):
        """
        :param custom_integer_validator: Function that takes the resolved value as only argument,
        and returns a str if validation fails, otherwise None
        """
        self._value_sdv = value_sdv
        self._custom_integer_validator = custom_integer_validator
        self._int_sdv = _IntResolver(value_sdv)
        self._validator = _ValidatorThatReportsViaExceptions(self._int_sdv, custom_integer_validator)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._value_sdv.references

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        self._validator.validate_pre_sds(environment)

    def resolve(self, symbols: SymbolTable) -> IntegerDdv:
        return IntegerDdv(self._value_sdv.resolve(symbols),
                          self._custom_integer_validator)


class _ValidatorThatReportsViaExceptions(SvhPreSdsValidatorViaExceptions):
    def __init__(self,
                 int_sdv: _IntResolver,
                 custom_integer_validator: Optional[CustomIntegerValidator]):
        self._int_sdv = int_sdv
        self._custom_integer_validator = custom_integer_validator

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):

        try:
            resolved_value = self._int_sdv.resolve(environment)
        except NotAnIntegerException as ex:
            py_ex_str = (
                ''
                if ex.python_exception_message is None
                else
                '\n\nPython exception:\n' + ex.python_exception_message
            )
            msg = text_docs.single_pre_formatted_line_object(
                str_constructor.FormatPositional(
                    'Argument must be an integer: `{}\'{}',
                    ex.value_string,
                    py_ex_str)
            )
            raise svh_exception.SvhValidationException(msg)

        self._validate_custom(resolved_value)

    def _validate_custom(self, resolved_value: int):
        if self._custom_integer_validator:
            err_msg = self._custom_integer_validator(resolved_value)
            if err_msg:
                raise svh_exception.SvhValidationException(err_msg)
