import unittest

from shellcheck_lib.instructions.setup.utils.instruction_utils import InstructionWithFileRefsBase
from shellcheck_lib.instructions.utils import file_ref
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.setup import SetupSettingsBuilder
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import home_and_eds_and_test_as_curr_dir, HomeAndEds
from shellcheck_lib_test.util.file_structure import DirContents
from shellcheck_lib_test.util.file_structure import empty_file


class TestInstruction(InstructionWithFileRefsBase):
    def __init__(self, file_ref_list_tuple):
        super().__init__(file_ref_list_tuple)

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()


class TestValidationShouldBeInPreValidateIfFileDoesExistPreEds(unittest.TestCase):
    def test_successful_validation(self):
        instruction = TestInstruction((file_ref.rel_home('file.txt'),))
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_eds:
            pre_validate = instruction.pre_validate(GlobalEnvironmentForPreEdsStep(home_and_eds.home_dir_path))
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.post_validate(env_from(home_and_eds))
            self.assertTrue(post_validate.is_success)

    def test_unsuccessful_validation(self):
        instruction = TestInstruction((file_ref.rel_home('non-existing-file.txt'),))
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            pre_validate = instruction.pre_validate(GlobalEnvironmentForPreEdsStep(home_and_eds.home_dir_path))
            self.assertFalse(pre_validate.is_success)

            post_validate = instruction.post_validate(env_from(home_and_eds))
            self.assertTrue(post_validate.is_success)


class TestValidationShouldBeInPostValidateIfFileDoesNotExistPreEds(unittest.TestCase):
    def test_successful_validation(self):
        instruction = TestInstruction((file_ref.rel_cwd('file.txt'),))
        with home_and_eds_and_test_as_curr_dir(
                eds_contents=act_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_eds:
            pre_validate = instruction.pre_validate(GlobalEnvironmentForPreEdsStep(home_and_eds.home_dir_path))
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.post_validate(env_from(home_and_eds))
            self.assertTrue(post_validate.is_success)

    def test_unsuccessful_validation(self):
        instruction = TestInstruction((file_ref.rel_cwd('file.txt'),))
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            pre_validate = instruction.pre_validate(GlobalEnvironmentForPreEdsStep(home_and_eds.home_dir_path))
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.post_validate(env_from(home_and_eds))
            self.assertFalse(post_validate.is_success)


def env_from(home_and_eds: HomeAndEds) -> GlobalEnvironmentForPostEdsPhase:
    return GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                            home_and_eds.eds)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestValidationShouldBeInPreValidateIfFileDoesExistPreEds))
    ret_val.addTest(unittest.makeSuite(TestValidationShouldBeInPostValidateIfFileDoesNotExistPreEds))
    return ret_val


if __name__ == '__main__':
    unittest.main()
