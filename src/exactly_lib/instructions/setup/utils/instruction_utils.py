from typing import Sequence

from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.test_case.result import svh
from exactly_lib.test_case_utils.path_check import PathCheck, pre_sds_validate, pre_or_post_sds_validate


class InstructionWithFileRefsBase(SetupPhaseInstruction):
    def __init__(self,
                 path_check_list: Sequence[PathCheck]):
        """
        :param path_check_list: Sequence of files to be validates
        """
        self.path_check_list = path_check_list

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        for path_check in self.path_check_list:
            assert isinstance(path_check, PathCheck)
            path = path_check.path_sdv.resolve(environment.symbols)
            if path.exists_pre_sds():
                result = pre_sds_validate(path_check, environment.path_resolving_environment)
                if not result.is_success:
                    return result
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        for path_check in self.path_check_list:
            assert isinstance(path_check, PathCheck)
            path = path_check.path_sdv.resolve(environment.symbols)
            if not path.exists_pre_sds():
                result = pre_or_post_sds_validate(path_check,
                                                  environment.path_resolving_environment_pre_or_post_sds)
                if not result.is_success:
                    return result
        return svh.new_svh_success()
