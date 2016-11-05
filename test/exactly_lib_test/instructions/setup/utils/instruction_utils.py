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
from exactly_lib_test.test_resources.execution.utils import home_and_eds_and_test_as_curr_dir, HomeAndSds


class TestInstruction(InstructionWithFileRefsBase):
    def __init__(self, file_ref_list_tuple):
        super().__init__(file_ref_list_tuple)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()


class TestValidationShouldBeInPreValidateIfFileDoesExistPreEds(unittest.TestCase):
    def test_successful_validation(self):
        instruction = TestInstruction((FileRefCheck(file_ref.rel_home('file.txt'),
                                                    FileCheckThatEvaluatesTo(True)),))
        with home_and_eds_and_test_as_curr_dir() as home_and_sds:
            pre_validate = instruction.validate_pre_sds(InstructionEnvironmentForPreSdsStep(home_and_sds.home_dir_path))
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_sds))
            self.assertTrue(post_validate.is_success)

    def test_unsuccessful_validation(self):
        instruction = TestInstruction((FileRefCheck(file_ref.rel_home('file.txt'),
                                                    FileCheckThatEvaluatesTo(False)),))
        with home_and_eds_and_test_as_curr_dir() as home_and_sds:
            pre_validate = instruction.validate_pre_sds(InstructionEnvironmentForPreSdsStep(home_and_sds.home_dir_path))
            self.assertFalse(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_sds))
            self.assertTrue(post_validate.is_success)


class TestValidationShouldBeInPostValidateIfFileDoesNotExistPreEds(unittest.TestCase):
    def test_successful_validation(self):
        instruction = TestInstruction((FileRefCheck(file_ref.rel_cwd('file.txt'),
                                                    FileCheckThatEvaluatesTo(True)),))
        with home_and_eds_and_test_as_curr_dir() as home_and_sds:
            pre_validate = instruction.validate_pre_sds(InstructionEnvironmentForPreSdsStep(home_and_sds.home_dir_path))
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_sds))
            self.assertTrue(post_validate.is_success)

    def test_unsuccessful_validation(self):
        instruction = TestInstruction((FileRefCheck(file_ref.rel_cwd('file.txt'),
                                                    FileCheckThatEvaluatesTo(False)),))
        with home_and_eds_and_test_as_curr_dir() as home_and_sds:
            pre_validate = instruction.validate_pre_sds(InstructionEnvironmentForPreSdsStep(home_and_sds.home_dir_path))
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_sds))
            self.assertFalse(post_validate.is_success)


def _env_from(home_and_sds: HomeAndSds) -> InstructionEnvironmentForPostSdsStep:
    return InstructionEnvironmentForPostSdsStep(home_and_sds.home_dir_path,
                                                home_and_sds.sds,
                                            'phase-identifier')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestValidationShouldBeInPreValidateIfFileDoesExistPreEds))
    ret_val.addTest(unittest.makeSuite(TestValidationShouldBeInPostValidateIfFileDoesNotExistPreEds))
    return ret_val


if __name__ == '__main__':
    unittest.main()
