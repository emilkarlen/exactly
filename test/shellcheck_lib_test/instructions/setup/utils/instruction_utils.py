import unittest

from shellcheck_lib.instructions.setup.utils.instruction_utils import InstructionWithFileRefsBase
from shellcheck_lib.instructions.utils import file_ref
from shellcheck_lib.instructions.utils.file_ref_check import FileRefCheck
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.test_case.phases.setup import SetupSettingsBuilder
from shellcheck_lib_test.instructions.utils.file_properties import FileCheckThatEvaluatesTo
from shellcheck_lib_test.test_resources.execution.utils import home_and_eds_and_test_as_curr_dir, HomeAndEds


class TestInstruction(InstructionWithFileRefsBase):
    def __init__(self, file_ref_list_tuple):
        super().__init__(file_ref_list_tuple)

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()


class TestValidationShouldBeInPreValidateIfFileDoesExistPreEds(unittest.TestCase):
    def test_successful_validation(self):
        instruction = TestInstruction((FileRefCheck(file_ref.rel_home('file.txt'),
                                                    FileCheckThatEvaluatesTo(True)),))
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            pre_validate = instruction.validate_pre_eds(GlobalEnvironmentForPreEdsStep(home_and_eds.home_dir_path))
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_eds))
            self.assertTrue(post_validate.is_success)

    def test_unsuccessful_validation(self):
        instruction = TestInstruction((FileRefCheck(file_ref.rel_home('file.txt'),
                                                    FileCheckThatEvaluatesTo(False)),))
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            pre_validate = instruction.validate_pre_eds(GlobalEnvironmentForPreEdsStep(home_and_eds.home_dir_path))
            self.assertFalse(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_eds))
            self.assertTrue(post_validate.is_success)


class TestValidationShouldBeInPostValidateIfFileDoesNotExistPreEds(unittest.TestCase):
    def test_successful_validation(self):
        instruction = TestInstruction((FileRefCheck(file_ref.rel_cwd('file.txt'),
                                                    FileCheckThatEvaluatesTo(True)),))
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            pre_validate = instruction.validate_pre_eds(GlobalEnvironmentForPreEdsStep(home_and_eds.home_dir_path))
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_eds))
            self.assertTrue(post_validate.is_success)

    def test_unsuccessful_validation(self):
        instruction = TestInstruction((FileRefCheck(file_ref.rel_cwd('file.txt'),
                                                    FileCheckThatEvaluatesTo(False)),))
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            pre_validate = instruction.validate_pre_eds(GlobalEnvironmentForPreEdsStep(home_and_eds.home_dir_path))
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_eds))
            self.assertFalse(post_validate.is_success)


def _env_from(home_and_eds: HomeAndEds) -> GlobalEnvironmentForPostEdsPhase:
    return GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                            home_and_eds.eds,
                                            'phase-identifier')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestValidationShouldBeInPreValidateIfFileDoesExistPreEds))
    ret_val.addTest(unittest.makeSuite(TestValidationShouldBeInPostValidateIfFileDoesNotExistPreEds))
    return ret_val


if __name__ == '__main__':
    unittest.main()
