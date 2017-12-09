from exactly_lib.help_texts.instruction_arguments import NEGATION_ARGUMENT_STR
from exactly_lib.test_case_utils.err_msg.error_info import ErrorInfo
from exactly_lib.test_case_utils.err_msg.property_description import PropertyDescription
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.string import line_separated


class ActualInfo:
    def __init__(self,
                 single_line_value: str,
                 description_lines: list = ()):
        self.single_line_value = single_line_value
        self.description_lines = list(description_lines)

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


class DiffErrorInfo(ErrorInfo):
    def __init__(self,
                 property_description: PropertyDescription,
                 expectation_type: ExpectationType,
                 expected: str,
                 actual: ActualInfo):
        """
        :param property_description:  Describes the property that the failure relates to.
        :param expectation_type: if the check is positive or negative
        :param expected: single line description of the expected value (for positive ExpectationType)
        :param actual: The actual value that caused the failure.
        """
        self.expectation_type = expectation_type
        self.property_description = property_description
        self.expected = expected
        self.actual = actual

    def error_message(self) -> str:
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
