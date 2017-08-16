from exactly_lib.instructions.assert_.utils.negation_of_assertion import NEGATION_ARGUMENT_STR
from exactly_lib.instructions.utils.err_msg.property_description import PropertyDescription
from exactly_lib.instructions.utils.expectation_type import ExpectationType
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.string import line_separated


class ErrorMessageConstructor:
    def error_message_lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        raise NotImplementedError('abstract method')


class EmptyErrorMessage(ErrorMessageConstructor):
    def error_message_lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        return []


class ExpectedAndActualFailure:
    def __init__(self,
                 property_description: PropertyDescription,
                 expectation_type: ExpectationType,
                 expected: str,
                 actual: str,
                 description_of_actual: list):
        self.expectation_type = expectation_type
        self.property_description = property_description
        self.expected = expected
        self.actual = actual
        self.description_of_actual = description_of_actual

    def render(self) -> str:
        lines = []
        lines.append('Unexpected ' + self.property_description.name)
        if self.property_description.object_description_lines:
            lines.append('')
            lines.extend(self.property_description.object_description_lines)

        lines.append('')
        lines.extend(self._err_msg_expected_and_actual_lines())

        if self.description_of_actual:
            lines.append('')
            lines.extend(self.description_of_actual)

        return line_separated(lines)

    def _err_msg_expected_and_actual_lines(self) -> list:
        negation_str = self._negation_str()
        expected_str = negation_str + self.expected
        return ['Expected : ' + expected_str,
                'Actual   : ' + self.actual]

    def _negation_str(self) -> str:
        if self.expectation_type is ExpectationType.POSITIVE:
            return ''
        else:
            return NEGATION_ARGUMENT_STR + ' '
