import os
import unittest

from exactly_lib.instructions.utils.arg_parse import relative_path_options
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationBase, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.not_operator import NotOperatorInfo
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import svh_check, pfh_check
from exactly_lib_test.test_resources import home_and_sds_test
from exactly_lib_test.test_resources.execution.home_or_sds_populator import HomeOrSdsPopulator, \
    HomeOrSdsPopulatorForHomeContents, HomeOrSdsPopulatorForSdsContents
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents, tmp_user_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents

_SUB_DIR_OF_ACT_DIR_THAT_IS_CWD = 'test-cwd'


class _CwdPopulator(HomeOrSdsPopulator):
    def __init__(self, contents: DirContents):
        self.contents = contents

    def write_to(self, home_and_sds: HomeAndSds):
        sub_dir = _get_cwd_path_and_make_dir_if_not_exists(home_and_sds.sds)
        self.contents.write_to(sub_dir)


class RelativityOptionConfiguration:
    def __init__(self, cli_option: str):
        self._cli_option = cli_option

    @property
    def option_string(self) -> str:
        return self._cli_option

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        raise NotImplementedError()

    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        raise NotImplementedError()


class TestWithConfigurationAndRelativityOptionBase(TestWithConfigurationBase):
    def __init__(self,
                 instruction_configuration: InstructionTestConfiguration,
                 option_configuration: RelativityOptionConfiguration):
        super().__init__(instruction_configuration)
        self.rel_opt = option_configuration

    def shortDescription(self):
        return (str(type(self)) + ' /\n' +
                str(type(self.configuration)) + ' /\n' +
                str(type(self.rel_opt))
                )


class TestWithConfigurationAndRelativityOptionAndNegationBase(TestWithConfigurationBase):
    def __init__(self,
                 instruction_configuration: InstructionTestConfiguration,
                 option_configuration: RelativityOptionConfiguration,
                 is_negated: bool):
        super().__init__(instruction_configuration)
        self.rel_opt = option_configuration
        self.not_opt = NotOperatorInfo(is_negated)

    def shortDescription(self):
        return (str(type(self)) + ' /\n' +
                str(type(self.configuration)) + ' /\n' +
                str(type(self.rel_opt)) + ' /\n' +
                'is_negated=' + str(self.not_opt.is_negated)
                )


def suite_for__conf__rel_opts__negations(instruction_configuration: InstructionTestConfiguration,
                                         relativity_options: list,
                                         test_cases: list) -> unittest.TestSuite:
    def suite_for_option(option_configuration: RelativityOptionConfiguration) -> unittest.TestSuite:
        not_negated = [tc(instruction_configuration, option_configuration, False)
                       for tc in test_cases]
        negated = [tc(instruction_configuration, option_configuration, True)
                   for tc in test_cases]
        return unittest.TestSuite(not_negated + negated)

    return unittest.TestSuite([suite_for_option(relativity_option)
                               for relativity_option in relativity_options
                               ])


class RelativityOptionConfigurationForRelHome(RelativityOptionConfiguration):
    def __init__(self):
        super().__init__(relative_path_options.REL_HOME_OPTION)

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return HomeOrSdsPopulatorForHomeContents(contents)

    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        return Expectation(validation_pre_sds=svh_check.is_validation_error())


class RelativityOptionConfigurationForRelSdsBase(RelativityOptionConfiguration):
    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        return Expectation(main_result=pfh_check.is_fail())


class RelativityOptionConfigurationForRelCwd(RelativityOptionConfigurationForRelSdsBase):
    def __init__(self):
        super().__init__(relative_path_options.REL_CWD_OPTION)

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return _CwdPopulator(contents)


class RelativityOptionConfigurationForRelAct(RelativityOptionConfigurationForRelSdsBase):
    def __init__(self):
        super().__init__(relative_path_options.REL_ACT_OPTION)

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return HomeOrSdsPopulatorForSdsContents(act_dir_contents(contents))


class RelativityOptionConfigurationForRelTmp(RelativityOptionConfigurationForRelSdsBase):
    def __init__(self):
        super().__init__(relative_path_options.REL_TMP_OPTION)

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return HomeOrSdsPopulatorForSdsContents(tmp_user_dir_contents(contents))


def _get_cwd_path_and_make_dir_if_not_exists(sds: SandboxDirectoryStructure):
    ret_val = sds.act_dir / _SUB_DIR_OF_ACT_DIR_THAT_IS_CWD
    if not ret_val.exists():
        os.mkdir(str(ret_val))
    return ret_val


class MkSubDirOfActAndMakeItCurrentDirectory(home_and_sds_test.Action):
    def apply(self, home_and_sds: HomeAndSds):
        sub_dir = _get_cwd_path_and_make_dir_if_not_exists(home_and_sds.sds)
        os.chdir(str(sub_dir))
