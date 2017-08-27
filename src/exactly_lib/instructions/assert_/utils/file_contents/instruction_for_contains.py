import pathlib

from exactly_lib.instructions.assert_.utils.checker import Checker
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.util.expectation_type import ExpectationType


def checker_for(expectation_type: ExpectationType,
                failure_info_resolver: DiffFailureInfoResolver,
                expected_reg_ex) -> Checker:
    if expectation_type is ExpectationType.POSITIVE:
        return _FileCheckerForPositiveMatch(failure_info_resolver, expected_reg_ex)
    else:
        return _FileCheckerForNegativeMatch(failure_info_resolver, expected_reg_ex)


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


class _FileCheckerForPositiveMatch(FileChecker):
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


class _FileCheckerForNegativeMatch(FileChecker):
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
