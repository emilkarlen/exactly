import unittest

from exactly_lib.instructions.assert_.contents_of_file import ACTUAL_RELATIVITY_CONFIGURATION
from exactly_lib.test_case_file_structure.path_relativity import RelNonHomeOptionType
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    RelativityOptionConfigurationForRelCwdForTestCwdDir
from exactly_lib_test.instructions.test_resources import relativity_options as rel_opt
from exactly_lib_test.instructions.test_resources.relativity_options import \
    RelativityOptionConfiguration

RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE = [
    RelativityOptionConfigurationForRelCwdForTestCwdDir(),
    rel_opt.conf_rel_non_home(RelNonHomeOptionType.REL_ACT),
    rel_opt.conf_rel_non_home(RelNonHomeOptionType.REL_TMP),
    rel_opt.symbol_conf_rel_non_home(RelNonHomeOptionType.REL_TMP,
                                     'ACTUAL_FILE_SYMBOL',
                                     ACTUAL_RELATIVITY_CONFIGURATION.options.accepted_relativity_variants),
    # Test of default relativity is done by "generic" tests of equals -
    # i.e. code in the test resources that are used for all content-checking instructions.
]


def suite_for_all_relativity_options(instruction_configuration: InstructionTestConfiguration,
                                     test_cases: list) -> unittest.TestSuite:
    def suite_for_option(option_configuration: RelativityOptionConfiguration) -> unittest.TestSuite:
        return unittest.TestSuite([tc(instruction_configuration, option_configuration)
                                   for tc in test_cases])

    return unittest.TestSuite([suite_for_option(relativity_option_configuration)
                               for relativity_option_configuration in RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE])
