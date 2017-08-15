import types

from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions
from exactly_lib.instructions.assert_.utils.expression import comparators
from exactly_lib.instructions.assert_.utils.expression.comparators import ComparisonOperator
from exactly_lib.instructions.assert_.utils.negation_of_assertion import NEGATION_ARGUMENT_STR
from exactly_lib.instructions.utils import return_svh_via_exceptions
from exactly_lib.instructions.utils.expectation_type import ExpectationType
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.util.string import line_separated


class ActualValueResolver:
    def __init__(self, property_name: str):
        self.property_name = property_name

    @property
    def references(self) -> list:
        return []

    def validate_pre_sds(self,
                         environment: i.InstructionEnvironmentForPostSdsStep):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        pass

    def resolve(self,
                environment: i.InstructionEnvironmentForPostSdsStep,
                os_services: OsServices):
        """
        Reports errors by raising exceptions from `return_pfh_via_exceptions`
        """
        raise NotImplementedError('abstract method')


class IntegerResolver:
    def __init__(self,
                 value_resolver: StringResolver,
                 custom_integer_restriction: types.FunctionType = None):
        self.value_resolver = value_resolver
        self.custom_integer_restriction = custom_integer_restriction

    @property
    def references(self) -> list:
        return self.value_resolver.references

    def validate_pre_sds(self, environment: i.InstructionEnvironmentForPostSdsStep):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        resolved_value = self.resolve(environment)
        self._validate_custom(resolved_value)

    def resolve(self, environment: i.InstructionEnvironmentForPostSdsStep) -> int:
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


class ComparisonSetup:
    """A comparison operator, resolvers for left and right operands, and an `ExpectationType`"""
    def __init__(self,
                 expectation_type: ExpectationType,
                 actual_value_lhs: ActualValueResolver,
                 operator: comparators.ComparisonOperator,
                 integer_resolver_rhs: IntegerResolver):
        self.expectation_type = expectation_type
        self.actual_value_lhs = actual_value_lhs
        self.integer_resolver = integer_resolver_rhs
        self.operator = operator

    @property
    def references(self) -> list:
        return self.actual_value_lhs.references + self.integer_resolver.references

    def validate_pre_sds(self, environment: i.InstructionEnvironmentForPostSdsStep):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        self.actual_value_lhs.validate_pre_sds(environment)
        self.integer_resolver.validate_pre_sds(environment)


class ComparisonExecutor:
    def __init__(self,
                 property_name: str,
                 expectation_type: ExpectationType,
                 lhs_actual_property_value: int,
                 rhs: int,
                 operator: ComparisonOperator):
        self.property_name = property_name
        self.expectation_type = expectation_type
        self.lhs_actual_property_value = lhs_actual_property_value
        self.rhs = rhs
        self.operator = operator

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
        err_msg = self._unexpected_value_message()
        raise return_pfh_via_exceptions.PfhFailException(err_msg)

    def _unexpected_value_message(self):
        negation_str = self._negation_str()
        expected_str = self.operator.name + ' ' + str(self.rhs)
        return line_separated(['Unexpected {}'.format(self.property_name),
                               'Expected : {}{}'.format(negation_str, expected_str),
                               'Actual   : {}'.format(self.lhs_actual_property_value)])

    def _negation_str(self) -> str:
        if self.expectation_type is ExpectationType.POSITIVE:
            return ''
        else:
            return NEGATION_ARGUMENT_STR + ' '
