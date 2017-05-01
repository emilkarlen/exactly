import os
import pathlib
import unittest

from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationBase, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.not_operator import NotOperatorInfo
from exactly_lib_test.instructions.test_resources.relativity_options import RelativityOptionConfigurationForRelSds, \
    RelativityOptionConfiguration
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import SdsPopulator
from exactly_lib_test.test_resources.file_structure import DirContents
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction

_SUB_DIR_OF_ACT_DIR_THAT_IS_CWD = 'test-cwd'


class _CwdPopulator(SdsPopulator):
    def __init__(self, contents: DirContents):
        self.contents = contents

    def apply(self, sds: SandboxDirectoryStructure):
        sub_dir = _get_cwd_path_and_make_dir_if_not_exists(sds)
        self.contents.write_to(sub_dir)


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


class RelativityOptionConfigurationForRelCwdForTestCwdDir(RelativityOptionConfigurationForRelSds):
    def __init__(self):
        super().__init__(file_ref_texts.REL_CWD_OPTION)

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return _test_cwd_dir(sds)

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return _CwdPopulator(contents)


def _get_cwd_path_and_make_dir_if_not_exists(sds: SandboxDirectoryStructure):
    ret_val = _test_cwd_dir(sds)
    if not ret_val.exists():
        os.mkdir(str(ret_val))
    return ret_val


class MkSubDirOfActAndMakeItCurrentDirectory(HomeAndSdsAction):
    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        sub_dir = _get_cwd_path_and_make_dir_if_not_exists(environment.sds)
        os.chdir(str(sub_dir))


def _test_cwd_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return sds.act_dir / _SUB_DIR_OF_ACT_DIR_THAT_IS_CWD
