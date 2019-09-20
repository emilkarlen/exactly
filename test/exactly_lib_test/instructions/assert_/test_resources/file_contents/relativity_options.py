import pathlib
import unittest

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelNonHomeOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationBase, InstructionTestConfiguration
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import NonHomePopulator
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_populators import \
    HomeOrSdsPopulator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    sub_dir_of_sds_contains_exactly
from exactly_lib_test.test_case_file_structure.test_resources.sds_populator import SdsPopulator, \
    SdsPopulatorForSubDir
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.misc import SUB_DIR_RESOLVER
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    pfh_expectation_type_config
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration, \
    RelativityOptionConfigurationForRelNonHome, \
    OptionStringConfigurationForRelativityOptionRelNonHome
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class TestWithConfigurationAndRelativityOptionAndNegationBase(TestWithConfigurationBase):
    def __init__(self,
                 instruction_configuration: InstructionTestConfiguration,
                 option_configuration: RelativityOptionConfiguration,
                 expectation_type: ExpectationType):
        super().__init__(instruction_configuration)
        self.rel_opt = option_configuration
        self.not_opt = pfh_expectation_type_config(expectation_type)

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

    @property
    def is_rel_cwd(self) -> bool:
        return True

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

    def assert_root_dir_contains_exactly(self, contents: DirContents) -> ValueAssertion:
        return sub_dir_of_sds_contains_exactly(SUB_DIR_RESOLVER.population_dir,
                                               contents)

    def population_dir(self, tds: HomeAndSds) -> pathlib.Path:
        return SUB_DIR_RESOLVER.population_dir(tds.sds)
