import types

from exactly_lib.instructions.assert_.utils.expression.comparison_structures import OperandResolver
from exactly_lib.instructions.utils import return_svh_via_exceptions
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep


class IntegerResolver(OperandResolver):
    def __init__(self,
                 property_name: str,
                 value_resolver: StringResolver,
                 custom_integer_restriction: types.FunctionType = None):
        super().__init__(property_name)
        self.value_resolver = value_resolver
        self.custom_integer_restriction = custom_integer_restriction

    @property
    def references(self) -> list:
        return self.value_resolver.references

    def validate_pre_sds(self, environment: InstructionEnvironmentForPostSdsStep):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        resolved_value = self.resolve(environment)
        self._validate_custom(resolved_value)

    def resolve(self, environment: InstructionEnvironmentForPostSdsStep) -> int:
        value_string = self.value_resolver.resolve(environment.symbols).value_when_no_dir_dependencies()
        try:
            return int(value_string)
        except ValueError:
            msg = 'Argument must be an integer: `{}\''.format(value_string)
            raise return_svh_via_exceptions.SvhValidationException(msg)

    def _validate_custom(self, resolved_value: int):
        if self.custom_integer_restriction:
            err_msg = self.custom_integer_restriction(resolved_value)
            if err_msg:
                raise return_svh_via_exceptions.SvhValidationException(err_msg)
