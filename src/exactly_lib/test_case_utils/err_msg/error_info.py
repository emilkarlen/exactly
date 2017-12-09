from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.util.string import line_separated


class ErrorInfo:
    def error_message(self) -> str:
        raise NotImplementedError('abstract method')

    def as_pfh_fail(self) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_fail(self.error_message())


class ExplanationErrorInfo(ErrorInfo):
    def __init__(self,
                 explanation: str,
                 object_description_lines: list):
        """
        :param object_description_lines: Describes the object that the failure relates to.
        :param explanation: A single line explanation of the cause of the failure.
        """
        self.explanation = explanation
        self.object_description_lines = object_description_lines

    def error_message(self) -> str:
        lines = []
        lines.append(self.explanation)
        if self.object_description_lines:
            lines.append('')
            lines.extend(self.object_description_lines)

        return line_separated(lines)


class ErrorMessagePartConstructor:
    """Constructs lines that are a part of an error message."""

    def lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        """
        :return: empty list if there is nothing to say
        """
        raise NotImplementedError('abstract method')


class NoErrorMessagePartConstructor(ErrorMessagePartConstructor):
    def lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        return []


class MultipleErrorMessagePartConstructor(ErrorMessagePartConstructor):
    def __init__(self,
                 separator_lines: list,
                 constructors: list):
        for c in constructors:
            pass
        self.separator_lines = tuple(separator_lines)
        self.constructors = tuple(constructors)

    def lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:

        ret_val = []

        for constructor in self.constructors:
            lines = constructor.lines(environment)
            if lines:
                if ret_val:
                    ret_val.extend(self.separator_lines)
                ret_val.extend(lines)

        return ret_val
