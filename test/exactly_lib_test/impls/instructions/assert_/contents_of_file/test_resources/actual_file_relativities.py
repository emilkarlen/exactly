from exactly_lib.impls.instructions.assert_.contents_of_file import ACTUAL_RELATIVITY_CONFIGURATION
from exactly_lib.tcfs.path_relativity import RelNonHdsOptionType, RelOptionType
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.relativity_options import \
    RelativityOptionConfigurationForRelCwdForTestCwdDir
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt

RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE = [
    RelativityOptionConfigurationForRelCwdForTestCwdDir(),
    rel_opt.conf_rel_non_hds(RelNonHdsOptionType.REL_ACT),
    rel_opt.conf_rel_non_hds(RelNonHdsOptionType.REL_TMP),
    rel_opt.symbol_conf_rel_any(RelOptionType.REL_TMP,
                                'ACTUAL_FILE_SYMBOL',
                                ACTUAL_RELATIVITY_CONFIGURATION.options.accepted_relativity_variants),
    # Test of default relativity is done by "generic" tests of equals -
    # i.e. code in the test resources that are used for all content-checking instructions.
]
