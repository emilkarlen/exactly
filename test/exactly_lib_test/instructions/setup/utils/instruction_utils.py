import os
import unittest

from exactly_lib.instructions.setup.utils.instruction_utils import InstructionWithFileRefsBase
from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.file_ref_check import FileRefCheck
from exactly_lib.type_system_values import file_refs
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsFixedPath
from exactly_lib_test.test_case_utils.file_properties import FileCheckThatEvaluatesTo
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestValidationShouldBeInPreValidateIfFileDoesExistPreSds))
    ret_val.addTest(unittest.makeSuite(TestValidationShouldBeInPostValidateIfFileDoesNotExistPreSds))
    return ret_val


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
        instruction = TestInstruction((FileRefCheck(_resolver_of(file_refs.rel_home(PathPartAsFixedPath('file.txt'))),
                                                    FileCheckThatEvaluatesTo(True)),))
        with home_and_sds_with_act_as_curr_dir() as path_resolving_env:
            home_and_sds = path_resolving_env.home_and_sds
            environment = InstructionEnvironmentForPreSdsStep(home_and_sds.hds, dict(os.environ))
            pre_validate = instruction.validate_pre_sds(environment)
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_sds, environment))
            self.assertTrue(post_validate.is_success)

    def test_unsuccessful_validation(self):
        instruction = TestInstruction((FileRefCheck(_resolver_of(file_refs.rel_home(PathPartAsFixedPath('file.txt'))),
                                                    FileCheckThatEvaluatesTo(False)),))
        with home_and_sds_with_act_as_curr_dir() as path_resolving_env:
            home_and_sds = path_resolving_env.home_and_sds
            environment = InstructionEnvironmentForPreSdsStep(home_and_sds.hds, dict(os.environ))
            pre_validate = instruction.validate_pre_sds(environment)
            self.assertFalse(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_sds, environment))
            self.assertTrue(post_validate.is_success)


class TestValidationShouldBeInPostValidateIfFileDoesNotExistPreSds(unittest.TestCase):
    def test_successful_validation(self):
        instruction = TestInstruction((FileRefCheck(_resolver_of(file_refs.rel_cwd(PathPartAsFixedPath('file.txt'))),
                                                    FileCheckThatEvaluatesTo(True)),))
        with home_and_sds_with_act_as_curr_dir() as path_resolving_env:
            home_and_sds = path_resolving_env.home_and_sds
            environment = InstructionEnvironmentForPreSdsStep(home_and_sds.hds, dict(os.environ))
            pre_validate = instruction.validate_pre_sds(environment)
            self.assertTrue(pre_validate.is_success)

            post_validate = instruction.validate_post_setup(_env_from(home_and_sds, environment))
            self.assertTrue(post_validate.is_success)

    def test_unsuccessful_validation(self):
        instruction = TestInstruction((FileRefCheck(_resolver_of(file_refs.rel_cwd(PathPartAsFixedPath('file.txt'))),
                                                    FileCheckThatEvaluatesTo(False)),))
        with home_and_sds_with_act_as_curr_dir() as path_resolving_env:
            home_and_sds = path_resolving_env.home_and_sds
            environment = InstructionEnvironmentForPreSdsStep(home_and_sds.hds, dict(os.environ))
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


def _resolver_of(file_ref: file_refs.FileRef) -> FileRefResolver:
    return FileRefConstant(file_ref)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
