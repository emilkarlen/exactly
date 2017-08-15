from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions
from exactly_lib.instructions.assert_.utils.expression import comparators
from exactly_lib.instructions.assert_.utils.expression.comparators import ComparisonOperator
from exactly_lib.instructions.assert_.utils.negation_of_assertion import NEGATION_ARGUMENT_STR
from exactly_lib.instructions.utils.expectation_type import ExpectationType
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.string import line_separated


class OperandResolver:
    """Resolves an operand used in a comparision"""

    def __init__(self, property_name: str):
        self.property_name = property_name

    @property
    def references(self) -> list:
        return []

    def validate_pre_sds(self, environment: InstructionEnvironmentForPostSdsStep):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        pass

    def resolve(self, environment: InstructionEnvironmentForPostSdsStep):
        """
        Reports errors by raising exceptions from `return_pfh_via_exceptions`
        
        :returns The value that can be used as one of the operands in a comparision.
        """
        raise NotImplementedError('abstract method')


class ComparisonHandler:
    """A comparison operator, resolvers for left and right operands, and an `ExpectationType`"""

    def __init__(self,
                 expectation_type: ExpectationType,
                 actual_value_lhs: OperandResolver,
                 operator: comparators.ComparisonOperator,
                 expected_value_rhs: OperandResolver):
        self.expectation_type = expectation_type
        self.actual_value_lhs = actual_value_lhs
        self.integer_resolver = expected_value_rhs
        self.operator = operator

    @property
    def references(self) -> list:
        return self.actual_value_lhs.references + self.integer_resolver.references

    def validate_pre_sds(self, environment: InstructionEnvironmentForPostSdsStep):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        self.actual_value_lhs.validate_pre_sds(environment)
        self.integer_resolver.validate_pre_sds(environment)

    def execute(self, environment: InstructionEnvironmentForPostSdsStep):
        """
        Reports failure by raising exceptions from `return_efh_via_exceptions`
        """
        lhs = self.actual_value_lhs.resolve(environment)
        rhs = self.integer_resolver.resolve(environment)
        executor = _ComparisonExecutor(
            self.actual_value_lhs.property_name,
            self.expectation_type,
            lhs,
            rhs,
            self.operator)
        executor.execute_and_return_pfh_via_exceptions()


class _ComparisonExecutor:
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
