import pathlib
import unittest
from typing import List, Callable, Sequence

from exactly_lib.tcfs.path_relativity import RelNonHdsOptionType
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.impls.types.string_matcher.test_resources.test_configuration import \
    TestCaseBase
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success
from exactly_lib_test.impls.types.test_resources.relativity_options import RelativityOptionConfiguration, \
    RelativityOptionConfigurationForRelNonHds, \
    OptionStringConfigurationForRelativityOptionRelNonHds
from exactly_lib_test.tcfs.test_resources.dir_populator import NonHdsPopulator
from exactly_lib_test.tcfs.test_resources.sds_check.sds_contents_check import \
    sub_dir_of_sds_contains_exactly
from exactly_lib_test.tcfs.test_resources.sds_populator import SdsPopulator, \
    SdsPopulatorForSubDir
from exactly_lib_test.tcfs.test_resources.sub_dir_of_sds_act import SUB_DIR_RESOLVER
from exactly_lib_test.tcfs.test_resources.tcds_populators import \
    TcdsPopulator
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class TestWithRelativityOptionAndNegationBase(TestCaseBase):
    def __init__(self,
                 option_configuration: RelativityOptionConfiguration,
                 expectation_type: ExpectationType):
        super().__init__()
        self.rel_opt = option_configuration
        self.not_opt = expectation_type_config__non_is_success(expectation_type)

    def shortDescription(self):
        return (str(type(self)) + ' /\n' +
                str(type(self.rel_opt)) + ' /\n' +
                str(self.not_opt)
                )


def suite_for__rel_opts__negations(
        relativity_options: List[RelativityOptionConfiguration],
        test_cases: Sequence[Callable[[RelativityOptionConfiguration, ExpectationType], unittest.TestCase]]
) -> unittest.TestSuite:
    def suite_for_option(option_configuration: RelativityOptionConfiguration) -> unittest.TestSuite:
        not_negated = [tc(option_configuration, ExpectationType.POSITIVE)
                       for tc in test_cases]
        negated = [tc(option_configuration, ExpectationType.POSITIVE)
                   for tc in test_cases]
        return unittest.TestSuite(not_negated + negated)

    return unittest.TestSuite([suite_for_option(relativity_option)
                               for relativity_option in relativity_options
                               ])


class RelativityOptionConfigurationForRelCwdForTestCwdDir(RelativityOptionConfigurationForRelNonHds):
    def __init__(self):
        super().__init__(OptionStringConfigurationForRelativityOptionRelNonHds(RelNonHdsOptionType.REL_CWD))

    @property
    def exists_pre_sds(self) -> bool:
        return False

    @property
    def is_rel_cwd(self) -> bool:
        return True

    def root_dir__non_hds(self, sds: SandboxDs) -> pathlib.Path:
        return self.root_dir__sds(sds)

    def populator_for_relativity_option_root(self, contents: DirContents) -> TcdsPopulator:
        return self.populator_for_relativity_option_root__sds(contents)

    def populator_for_relativity_option_root__non_hds(self,
                                                      contents: DirContents) -> NonHdsPopulator:
        return self.populator_for_relativity_option_root__sds(contents)

    def root_dir__sds(self, sds: SandboxDs) -> pathlib.Path:
        return SUB_DIR_RESOLVER.population_dir(sds)

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return SdsPopulatorForSubDir(SUB_DIR_RESOLVER, contents)

    def assert_root_dir_contains_exactly(self, contents: DirContents) -> Assertion:
        return sub_dir_of_sds_contains_exactly(SUB_DIR_RESOLVER.population_dir,
                                               contents)

    def population_dir(self, tds: TestCaseDs) -> pathlib.Path:
        return SUB_DIR_RESOLVER.population_dir(tds.sds)
