import pathlib
import shlex

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general import line_source
from shellcheck_lib.test_case import instructions as i
from shellcheck_lib.instructions.instruction_parser_for_single_phase2 import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException
from . import utils


class Instruction(utils.InstructionWithoutValidationBase):
    def __init__(self,
                 expected_value: int):
        self._expected_value = expected_value

    def main(self,
             global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.PassOrFailOrHardError:
        actual_value = read_exitcode(global_environment.eds)
        if actual_value == self._expected_value:
            return i.new_pfh_pass()
        return i.new_pfh_fail('Unexpected exitcode. Expected:%d, actual:%d' % (self._expected_value,
                                                                               actual_value))


class Parser(SingleInstructionParser):
    def apply(self,
              source: line_source.LineSequenceBuilder,
              instruction_argument: str) -> Instruction:
        argument_list = shlex.split(instruction_argument)
        if len(argument_list) != 1:
            raise SingleInstructionInvalidArgumentException('Exactly 1 argument expected, got ' +
                                                            str(len(argument_list)))
        try:
            expected = int(argument_list[0])
        except ValueError:
            raise SingleInstructionInvalidArgumentException('Argument must be an integer')

        if expected < 0 or expected > 255:
            raise SingleInstructionInvalidArgumentException('Argument must be an integer in the range [0, 255]')

        return Instruction(expected)


class InstructionEnvironmentError(Exception):
    def __init__(self,
                 error_message: str):
        super().__init__()
        self.error_message = error_message

    def __str__(self):
        return self.error_message


class FileOpenEnvironmentError(InstructionEnvironmentError):
    def __init__(self,
                 file_purpose: str,
                 path: pathlib.Path):
        super().__init__('Failed to open file for %s: %s' %
                         (file_purpose, str(path)))


def read_exitcode(eds: ExecutionDirectoryStructure) -> int:
    try:
        f = eds.result.exitcode_file.open()
    except IOError:
        raise FileOpenEnvironmentError('Exit Code', eds.result.exitcode_file)
    try:
        contents = f.read()
        return int(contents)
    except IOError:
        raise InstructionEnvironmentError('Failed to read contents from %s' % str(eds.result.exitcode_file))
    except ValueError:
        msg = 'The contents of the file for Exit Code ("%s") is not an integer: "%s"' % (str(eds.result.exitcode_file),
                                                                                         contents)
        raise InstructionEnvironmentError(msg)
    finally:
        f.close()
