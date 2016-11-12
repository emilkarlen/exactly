import os
import unittest

from exactly_lib.instructions.setup.utils.instruction_utils import InstructionWithFileRefsBase
from exactly_lib.instructions.utils import file_ref
from exactly_lib.instructions.utils.file_ref_check import FileRefCheck
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib_test.instructions.utils.file_properties import FileCheckThatEvaluatesTo
from exactly_lib_test.test_resources.execution.utils import home_and_sds_and_test_as_curr_dir, HomeAndSds


class TestInstruction(InstructionWithFileRefsBase):
    def __init__(self, file_ref_list_tuple):
        super().__init__(file_ref_list_tuple)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()


class TestValidationShouldBeInPreValidateIfFileDoesExistPreSds(unittest.TestCase):
    def test_successful_validation(self):
        instruction = TestInstruction((FileRefCheck(file_ref.rel_home('file.txt'),
                                                    FileCheckThatEvaluatesTo(True)),))
        with home_and_sds_and_test_as_curr_dir() as home_and_sds:
            environment = InstructionEnvironmentForPreSdsStep(home_and_sds.home_dir_path, dict(os.environ))
            pre_validate = instruction.validate_pre_sds(environment)
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_sds, environment))
            self.assertTrue(post_validate.is_success)

    def test_unsuccessful_validation(self):
        instruction = TestInstruction((FileRefCheck(file_ref.rel_home('file.txt'),
                                                    FileCheckThatEvaluatesTo(False)),))
        with home_and_sds_and_test_as_curr_dir() as home_and_sds:
            environment = InstructionEnvironmentForPreSdsStep(home_and_sds.home_dir_path, dict(os.environ))
            pre_validate = instruction.validate_pre_sds(environment)
            self.assertFalse(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_sds, environment))
            self.assertTrue(post_validate.is_success)


class TestValidationShouldBeInPostValidateIfFileDoesNotExistPreSds(unittest.TestCase):
    def test_successful_validation(self):
        instruction = TestInstruction((FileRefCheck(file_ref.rel_cwd('file.txt'),
                                                    FileCheckThatEvaluatesTo(True)),))
        with home_and_sds_and_test_as_curr_dir() as home_and_sds:
            environment = InstructionEnvironmentForPreSdsStep(home_and_sds.home_dir_path, dict(os.environ))
            pre_validate = instruction.validate_pre_sds(environment)
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_sds, environment))
            self.assertTrue(post_validate.is_success)

    def test_unsuccessful_validation(self):
        instruction = TestInstruction((FileRefCheck(file_ref.rel_cwd('file.txt'),
                                                    FileCheckThatEvaluatesTo(False)),))
        with home_and_sds_and_test_as_curr_dir() as home_and_sds:
            environment = InstructionEnvironmentForPreSdsStep(home_and_sds.home_dir_path, dict(os.environ))
            pre_validate = instruction.validate_pre_sds(environment)
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_sds, environment))
            self.assertFalse(post_validate.is_success)


def _env_from(home_and_sds: HomeAndSds,
              environment: InstructionEnvironmentForPreSdsStep) -> InstructionEnvironmentForPostSdsStep:
    return InstructionEnvironmentForPostSdsStep(environment.home_directory,
                                                environment.environ,
                                                home_and_sds.sds,
                                                'phase-identifier')


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestValidationShouldBeInPreValidateIfFileDoesExistPreSds))
    ret_val.addTest(unittest.makeSuite(TestValidationShouldBeInPostValidateIfFileDoesNotExistPreSds))
    return ret_val


def run_suite():
    unittest.TextTestRunner().run(suite())

if __name__ == '__main__':
    run_suite()
