import unittest

from exactly_lib.appl_env.os_services import OsServices
from exactly_lib.instructions.setup.utils.instruction_utils import InstructionWithFileRefsBase
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib.test_case.result import sh
from exactly_lib.test_case_utils.path_check import PathCheck
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_case_utils.file_properties import FileCheckThatEvaluatesTo
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestValidationShouldBeInPreValidateIfFileDoesExistPreSds))
    ret_val.addTest(unittest.makeSuite(TestValidationShouldBeInPostValidateIfFileDoesNotExistPreSds))
    return ret_val


class TestInstruction(InstructionWithFileRefsBase):
    def __init__(self, path_list_tuple):
        super().__init__(path_list_tuple)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()


class TestValidationShouldBeInPreValidateIfFileDoesExistPreSds(unittest.TestCase):
    def test_successful_validation(self):
        instruction = TestInstruction(
            (PathCheck(_sdv_of(path_ddvs.rel_hds_case(path_ddvs.constant_path_part('file.txt'))),
                       FileCheckThatEvaluatesTo(True)),))
        with tcds_with_act_as_curr_dir() as path_resolving_env:
            tcds = path_resolving_env.tcds
            environment = InstructionEnvironmentForPreSdsStep(tcds.hds, ProcessExecutionSettings.with_empty_environ())
            pre_validate = instruction.validate_pre_sds(environment)
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(tcds.sds, environment))
            self.assertTrue(post_validate.is_success)

    def test_unsuccessful_validation(self):
        instruction = TestInstruction(
            (PathCheck(_sdv_of(path_ddvs.rel_hds_case(path_ddvs.constant_path_part('file.txt'))),
                       FileCheckThatEvaluatesTo(False)),))
        with tcds_with_act_as_curr_dir() as path_resolving_env:
            tcds = path_resolving_env.tcds
            environment = InstructionEnvironmentForPreSdsStep(tcds.hds, ProcessExecutionSettings.with_empty_environ())
            pre_validate = instruction.validate_pre_sds(environment)
            self.assertFalse(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(tcds.sds, environment))
            self.assertTrue(post_validate.is_success)


class TestValidationShouldBeInPostValidateIfFileDoesNotExistPreSds(unittest.TestCase):
    def test_successful_validation(self):
        instruction = TestInstruction(
            (PathCheck(_sdv_of(path_ddvs.rel_cwd(path_ddvs.constant_path_part('file.txt'))),
                       FileCheckThatEvaluatesTo(True)),))
        with tcds_with_act_as_curr_dir() as path_resolving_env:
            tcds = path_resolving_env.tcds
            environment = InstructionEnvironmentForPreSdsStep(tcds.hds, ProcessExecutionSettings.with_empty_environ())
            pre_validate = instruction.validate_pre_sds(environment)
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(tcds.sds, environment))
            self.assertTrue(post_validate.is_success)

    def test_unsuccessful_validation(self):
        instruction = TestInstruction(
            (PathCheck(_sdv_of(path_ddvs.rel_cwd(path_ddvs.constant_path_part('file.txt'))),
                       FileCheckThatEvaluatesTo(False)),))
        with tcds_with_act_as_curr_dir() as path_resolving_env:
            tcds = path_resolving_env.tcds
            environment = InstructionEnvironmentForPreSdsStep(tcds.hds, ProcessExecutionSettings.with_empty_environ())
            pre_validate = instruction.validate_pre_sds(environment)
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(tcds.sds, environment))
            self.assertFalse(post_validate.is_success)


def _env_from(sds: SandboxDs,
              environment: InstructionEnvironmentForPreSdsStep) -> InstructionEnvironmentForPostSdsStep:
    return InstructionEnvironmentPostSdsBuilder.new_from_pre_sds(
        environment,
        sds,
    ).build_post_sds()


def _sdv_of(path: path_ddvs.PathDdv) -> PathSdv:
    return path_sdvs.constant(path)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
