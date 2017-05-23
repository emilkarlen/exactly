import pathlib

from exactly_lib.instructions.assert_.utils.file_contents.actual_file_transformers import ActualFileTransformer
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import pfh


class FileChecker:
    def apply(self, actual_file_path: pathlib.Path) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()


class FileCheckerForPositiveMatch(FileChecker):
    def __init__(self, expected_reg_ex):
        self._expected_reg_ex = expected_reg_ex

    def apply(self, actual_file_path: pathlib.Path) -> pfh.PassOrFailOrHardError:
        actual_file_name = str(actual_file_path)
        with open(actual_file_name) as f:
            for line in f:
                if self._expected_reg_ex.search(line.rstrip('\n')):
                    return pfh.new_pfh_pass()
        return pfh.new_pfh_fail("No lines matching reg ex '{}'".format(self._expected_reg_ex.pattern))


class FileCheckerForNegativeMatch(FileChecker):
    def __init__(self, expected_reg_ex):
        self._expected_reg_ex = expected_reg_ex

    def apply(self, actual_file_path: pathlib.Path) -> pfh.PassOrFailOrHardError:
        actual_file_name = str(actual_file_path)
        with open(actual_file_name) as f:
            line_num = 1
            for line in f:
                plain_line = line.rstrip('\n')
                if self._expected_reg_ex.search(plain_line):
                    msg = "Line {} matches reg ex '{}':\n{}".format(line_num,
                                                                    self._expected_reg_ex.pattern,
                                                                    plain_line)
                    return pfh.new_pfh_fail(msg)
                line_num += 1
        return pfh.new_pfh_pass()


class ContainsAssertionInstruction(AssertPhaseInstruction):
    def __init__(self,
                 file_checker: FileChecker,
                 actual_contents: ComparisonActualFile,
                 actual_file_transformer: ActualFileTransformer):
        self._actual_value = actual_contents
        self._file_checker = file_checker
        self._actual_file_transformer = actual_file_transformer

    def symbol_usages(self) -> list:
        return self._actual_value.symbol_usages

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        actual_file_path = self._actual_value.file_path(environment)
        failure_message = self._actual_value.file_check_failure(environment)
        if failure_message is not None:
            return pfh.new_pfh_fail(failure_message)
        processed_actual_file_path = self._actual_file_transformer.transform(environment,
                                                                             os_services,
                                                                             actual_file_path)
        return self._file_checker.apply(processed_actual_file_path)
