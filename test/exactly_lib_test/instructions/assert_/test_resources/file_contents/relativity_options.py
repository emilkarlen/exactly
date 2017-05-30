import os
import pathlib
import unittest

from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.path_relativity import RelNonHomeOptionType, RelSdsOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationBase, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.not_operator import NotOperatorInfo
from exactly_lib_test.instructions.test_resources.relativity_options import RelativityOptionConfiguration, \
    RelativityOptionConfigurationForRelNonHome, \
    OptionStringConfigurationForRelativityOptionRelNonHome
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import NonHomePopulator
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import \
    HomeOrSdsPopulator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import SdsPopulator, \
    SdsSubDirResolver, SdsPopulatorForSubDir
from exactly_lib_test.test_resources.file_structure import DirContents
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction

_SUB_DIR_OF_ACT_DIR_THAT_IS_CWD = 'test-cwd'

SUB_DIR_RESOLVER = SdsSubDirResolver(RelSdsOptionType.REL_ACT,
                                     _SUB_DIR_OF_ACT_DIR_THAT_IS_CWD)


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


class RelativityOptionConfigurationForRelCwdForTestCwdDir(RelativityOptionConfigurationForRelNonHome):
    def __init__(self):
        super().__init__(OptionStringConfigurationForRelativityOptionRelNonHome(RelNonHomeOptionType.REL_CWD))

    @property
    def exists_pre_sds(self) -> bool:
        return False

    def root_dir__non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.root_dir__sds(sds)

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        return self.populator_for_relativity_option_root__sds(contents)

    def populator_for_relativity_option_root__non_home(self,
                                                       contents: DirContents) -> NonHomePopulator:
        return self.populator_for_relativity_option_root__sds(contents)

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return SUB_DIR_RESOLVER.population_dir(sds)

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return SdsPopulatorForSubDir(SUB_DIR_RESOLVER, contents)


def _get_cwd_path_and_make_dir_if_not_exists(sds: SandboxDirectoryStructure):
    ret_val = SUB_DIR_RESOLVER.population_dir(sds)
    ret_val.mkdir(parents=True,
                  exist_ok=True)
    return ret_val


class MkSubDirOfActAndMakeItCurrentDirectory(HomeAndSdsAction):
    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        sub_dir = _get_cwd_path_and_make_dir_if_not_exists(environment.sds)
        os.chdir(str(sub_dir))
