import types

from exactly_lib.instructions.assert_.utils.expression.comparison_structures import OperandResolver
from exactly_lib.instructions.utils import return_svh_via_exceptions
from exactly_lib.named_element.symbol.string_resolver import StringResolver
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep


class IntegerResolver(OperandResolver):
    def __init__(self,
                 property_name: str,
                 value_resolver: StringResolver,
                 custom_integer_validator: types.FunctionType = None):
        """

        :param property_name:
        :param value_resolver:
        :param custom_integer_validator: Function that takes the resolved value as only argument,
        and returns a str if validation fails, otherwise None
        """
        super().__init__(property_name)
        self.value_resolver = value_resolver
        self.custom_integer_validator = custom_integer_validator

    @property
    def references(self) -> list:
        return self.value_resolver.references

    def validate_pre_sds(self, environment: InstructionEnvironmentForPreSdsStep):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """

        # TODO Implement this, or part of it, as a PreOrPostSdsValidator ??
        #
        # no not have time to look at this for the moment
        #
        # Bot this method, and custom_integer_restriction maybe should be implemented as PreOrPostSdsValidator,
        #
        # or maybe as a new kind of validator that only validates pre-sds

        try:
            resolved_value = self._resolve(environment)
        except NotAnIntegerException as ex:
            msg = 'Argument must be an integer: `{}\''.format(ex.value_string)
            raise return_svh_via_exceptions.SvhValidationException(msg)

        self._validate_custom(resolved_value)

    def resolve(self, environment: InstructionEnvironmentForPostSdsStep) -> int:
        try:
            return self._resolve(environment)
        except NotAnIntegerException as ex:
            msg = ('Argument is not an integer,'
                   ' even though this should have been checked by the validation: `{}\''.format(ex.value_string))
            raise return_svh_via_exceptions.SvhHardErrorException(msg)

    def _resolve(self, environment: InstructionEnvironmentForPreSdsStep) -> int:
        value_string = self.value_resolver.resolve(environment.symbols).value_when_no_dir_dependencies()
        try:
            val = eval(value_string)
            if isinstance(val, int):
                return val
            else:
                raise NotAnIntegerException(value_string)
        except SyntaxError:
            raise NotAnIntegerException(value_string)
        except ValueError:
            raise NotAnIntegerException(value_string)
        except NameError:
            raise NotAnIntegerException(value_string)

    def _validate_custom(self, resolved_value: int):
        if self.custom_integer_validator:
            err_msg = self.custom_integer_validator(resolved_value)
            if err_msg:
                raise return_svh_via_exceptions.SvhValidationException(err_msg)


class NotAnIntegerException(Exception):
    def __init__(self, value_string: str):
        self.value_string = value_string
