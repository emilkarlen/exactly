import pathlib

from exactly_lib.instructions.assert_.utils.checker import Checker
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.instruction_with_checkers import \
    instruction_with_exist_trans_and_checker
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformerResolver


class FileChecker(Checker):
    def __init__(self,
                 failure_info_resolver: DiffFailureInfoResolver,
                 expected_reg_ex):
        super().__init__()
        self._failure_info_resolver = failure_info_resolver
        self._expected_reg_ex = expected_reg_ex

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              actual_file_path: pathlib.Path):
        raise NotImplementedError()


def contains_assertion_instruction(actual_contents: ComparisonActualFile,
                                   actual_file_transformer_resolver: FileTransformerResolver,
                                   file_checker: FileChecker,
                                   ) -> AssertPhaseInstruction:
    return instruction_with_exist_trans_and_checker(
        actual_contents,
        actual_file_transformer_resolver,
        file_checker,
    )


class FileCheckerForPositiveMatch(FileChecker):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              actual_file_path: pathlib.Path):
        actual_file_name = str(actual_file_path)
        with open(actual_file_name) as f:
            for line in f:
                if self._expected_reg_ex.search(line.rstrip('\n')):
                    return
        failure_info = self._failure_info_resolver.resolve(environment,
                                                           diff_msg.actual_with_single_line_value('no line matches'))
        raise PfhFailException(failure_info.render())


class FileCheckerForNegativeMatch(FileChecker):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              actual_file_path: pathlib.Path):
        actual_file_name = str(actual_file_path)
        with open(actual_file_name) as f:
            line_num = 1
            for line in f:
                plain_line = line.rstrip('\n')
                if self._expected_reg_ex.search(plain_line):
                    single_line_actual_value = 'line {} matches'.format(line_num)
                    failure_info = self._failure_info_resolver.resolve(environment,
                                                                       diff_msg.actual_with_single_line_value(
                                                                           single_line_actual_value,
                                                                           [plain_line]))
                    raise PfhFailException(failure_info.render())
                line_num += 1
