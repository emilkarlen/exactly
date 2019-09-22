from typing import Sequence, Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPreOrPostSds, PathResolvingEnvironmentPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils import svh_exception
from exactly_lib.test_case_utils.condition.comparison_structures import OperandResolver
from exactly_lib.test_case_utils.condition.integer.evaluate_integer import NotAnIntegerException, python_evaluate
from exactly_lib.test_case_utils.condition.integer.integer_value import CustomIntegerValidator, IntegerValue
from exactly_lib.test_case_utils.validators import SvhPreSdsValidatorViaExceptions
from exactly_lib.util.simple_textstruct.rendering import strings
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
            msg = text_docs.single_pre_formatted_line_object(
                strings.FormatPositional(
                    'Argument is not an integer,'
                    ' even though this should have been checked by the validation: `{}\'',
                    ex.value_string)
            )
            raise svh_exception.SvhHardErrorException(msg)

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


class _PreOrPostSdsValidator(PreOrPostSdsValidator):
    def __init__(self, adapted: SvhPreSdsValidatorViaExceptions):
        self._adapted = adapted

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        try:
            self._adapted.validate_pre_sds(environment)
        except svh_exception.SvhException as ex:
            return ex.err_msg

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        return None
