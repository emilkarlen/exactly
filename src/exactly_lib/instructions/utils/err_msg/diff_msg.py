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


class ActualInfo:
    def __init__(self,
                 single_line_value: str,
                 description_lines: list):
        self.single_line_value = single_line_value
        self.description_lines = description_lines

    def has_single_line_value_str(self) -> bool:
        return self.single_line_value is not None

    def single_line_value_str(self) -> str:
        if self.single_line_value is None:
            return ''
        return self.single_line_value


def actual_with_single_line_value(single_line_value: str,
                                  description_lines: list = ()) -> ActualInfo:
    return ActualInfo(single_line_value, list(description_lines))


def actual_with_just_description_lines(description_lines: list) -> ActualInfo:
    return ActualInfo(None, list(description_lines))


class DiffFailureInfo:
    def __init__(self,
                 property_description: PropertyDescription,
                 expectation_type: ExpectationType,
                 expected: str,
                 actual: ActualInfo):
        self.expectation_type = expectation_type
        self.property_description = property_description
        self.expected = expected
        self.actual = actual

    def render(self) -> str:
        lines = []
        lines.append('Unexpected ' + self.property_description.name)
        if self.property_description.object_description_lines:
            lines.append('')
            lines.extend(self.property_description.object_description_lines)

        lines.append('')
        lines.extend(self._err_msg_expected_and_actual_lines())

        if self.actual.description_lines:
            lines.append('')
            lines.extend(self.actual.description_lines)

        return line_separated(lines)

    def _err_msg_expected_and_actual_lines(self) -> list:
        negation_str = self._negation_str()
        expected_str = negation_str + self.expected

        ret_val = [_EXPECTED_HEADER + expected_str]

        if self.actual.has_single_line_value_str():
            ret_val.append(_ACTUAL_HEADER + self.actual.single_line_value)

        return ret_val

    def _negation_str(self) -> str:
        if self.expectation_type is ExpectationType.POSITIVE:
            return ''
        else:
            return NEGATION_ARGUMENT_STR + ' '


_EXPECTED_HEADER = 'Expected : '
_ACTUAL_HEADER = 'Actual   : '
