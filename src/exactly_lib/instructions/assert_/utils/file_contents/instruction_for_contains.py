import pathlib

from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.utils.err_msg import diff_msg
from exactly_lib.instructions.utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case_utils.file_transformer.actual_file_transformer import ActualFileTransformerResolver


class FileChecker:
    def __init__(self,
                 failure_info_resolver: DiffFailureInfoResolver,
                 expected_reg_ex):
        self._failure_info_resolver = failure_info_resolver
        self._expected_reg_ex = expected_reg_ex

    def apply(self,
              environment: InstructionEnvironmentForPostSdsStep,
              actual_file_path: pathlib.Path) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()


class FileCheckerForPositiveMatch(FileChecker):
    def apply(self,
              environment: InstructionEnvironmentForPostSdsStep,
              actual_file_path: pathlib.Path) -> pfh.PassOrFailOrHardError:
        actual_file_name = str(actual_file_path)
        with open(actual_file_name) as f:
            for line in f:
                if self._expected_reg_ex.search(line.rstrip('\n')):
                    return pfh.new_pfh_pass()
        return self._failure_info_resolver.resolve(
            environment,
            diff_msg.actual_with_single_line_value('no line matches')).as_pfh_fail()


class FileCheckerForNegativeMatch(FileChecker):
    def apply(self,
              environment: InstructionEnvironmentForPostSdsStep,
              actual_file_path: pathlib.Path) -> pfh.PassOrFailOrHardError:
        actual_file_name = str(actual_file_path)
        with open(actual_file_name) as f:
            line_num = 1
            for line in f:
                plain_line = line.rstrip('\n')
                if self._expected_reg_ex.search(plain_line):
                    single_line_actual_value = 'line {} matches'.format(line_num)
                    return self._failure_info_resolver.resolve(
                        environment,
                        diff_msg.actual_with_single_line_value(single_line_actual_value,
                                                               [plain_line])
                    ).as_pfh_fail()
                line_num += 1
        return pfh.new_pfh_pass()


class ContainsAssertionInstruction(AssertPhaseInstruction):
    def __init__(self,
                 file_checker: FileChecker,
                 actual_contents: ComparisonActualFile,
                 actual_file_transformer_resolver: ActualFileTransformerResolver):
        self._actual_value = actual_contents
        self._file_checker = file_checker
        self._actual_file_transformer_resolver = actual_file_transformer_resolver

    def symbol_usages(self) -> list:
        return self._actual_value.references

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        actual_file_path = self._actual_value.file_path(environment)
        failure_message = self._actual_value.file_check_failure(environment)
        if failure_message is not None:
            return pfh.new_pfh_fail(failure_message)
        actual_file_transformer = self._actual_file_transformer_resolver.resolve(environment.symbols)
        processed_actual_file_path = actual_file_transformer.transform(environment,
                                                                       os_services,
                                                                       actual_file_path)
        return self._file_checker.apply(environment, processed_actual_file_path)
