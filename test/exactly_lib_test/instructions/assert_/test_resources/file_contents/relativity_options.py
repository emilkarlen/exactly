import pathlib
import unittest

from exactly_lib.instructions.utils.expectation_type import ExpectationType
from exactly_lib.test_case_file_structure.path_relativity import RelNonHomeOptionType, RelSdsOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationBase, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.instruction_with_negation_argument import \
    ExpectationTypeConfig
from exactly_lib_test.instructions.test_resources.relativity_options import RelativityOptionConfiguration, \
    RelativityOptionConfigurationForRelNonHome, \
    OptionStringConfigurationForRelativityOptionRelNonHome
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import NonHomePopulator
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import \
    HomeOrSdsPopulator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import SdsPopulator, \
    SdsPopulatorForSubDir, SdsSubDirResolverWithRelSdsRoot
from exactly_lib_test.test_resources.file_structure import DirContents
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_actions import \
    MkSubDirAndMakeItCurrentDirectory

_SUB_DIR_OF_ACT_DIR_THAT_IS_CWD = 'test-cwd'

SUB_DIR_RESOLVER = SdsSubDirResolverWithRelSdsRoot(RelSdsOptionType.REL_ACT,
                                                   _SUB_DIR_OF_ACT_DIR_THAT_IS_CWD)


class TestWithConfigurationAndRelativityOptionAndNegationBase(TestWithConfigurationBase):
    def __init__(self,
                 instruction_configuration: InstructionTestConfiguration,
                 option_configuration: RelativityOptionConfiguration,
                 expectation_type: ExpectationType):
        super().__init__(instruction_configuration)
        self.rel_opt = option_configuration
        self.not_opt = ExpectationTypeConfig(expectation_type)

    def shortDescription(self):
        return (str(type(self)) + ' /\n' +
                str(type(self.configuration)) + ' /\n' +
                str(type(self.rel_opt)) + ' /\n' +
                str(self.not_opt)
                )


def suite_for__conf__rel_opts__negations(instruction_configuration: InstructionTestConfiguration,
                                         relativity_options: list,
                                         test_cases: list) -> unittest.TestSuite:
    def suite_for_option(option_configuration: RelativityOptionConfiguration) -> unittest.TestSuite:
        not_negated = [tc(instruction_configuration, option_configuration, ExpectationType.POSITIVE)
                       for tc in test_cases]
        negated = [tc(instruction_configuration, option_configuration, ExpectationType.POSITIVE)
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


MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY = MkSubDirAndMakeItCurrentDirectory(SUB_DIR_RESOLVER)
