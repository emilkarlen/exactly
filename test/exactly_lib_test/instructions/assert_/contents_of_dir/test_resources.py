import unittest

from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelHomeOptionType, \
    PathRelativityVariants, RelOptionType
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.check_with_neg_and_rel_opts import \
    InstructionChecker, InstructionArgumentsVariantConstructor
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check as asrt_pfh
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, sym_link
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_actions import \
    MkSubDirAndMakeItCurrentDirectory


class TheInstructionArgumentsVariantConstructorForNotAndRelOpt(InstructionArgumentsVariantConstructor):
    """
    Constructs the instruction argument for a given negation-option config
    and rel-opt config.
    """

    def apply(self,
              etc: ExpectationTypeConfig,
              rel_opt_config: RelativityOptionConfiguration,
              ) -> str:
        ret_val = self.instruction_argument_template.replace('<rel_opt>', rel_opt_config.option_string)
        ret_val = replace_not_op(etc, ret_val)
        return ret_val


def replace_not_op(etc: ExpectationTypeConfig, s: str) -> str:
    return s.replace('<not_opt>', etc.nothing__if_positive__not_option__if_negative)


class TestCaseBaseForParser(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.checker = InstructionChecker(
            self,
            sut.Parser(),
            ACCEPTED_REL_OPT_CONFIGURATIONS,
        )


class TestCommonFailureConditionsBase:
    @property
    def _checker(self) -> InstructionChecker:
        return InstructionChecker(
            self._get_unittest_test_case(),
            sut.Parser(),
            ACCEPTED_REL_OPT_CONFIGURATIONS,
        )

    def _get_unittest_test_case(self) -> unittest.TestCase:
        raise NotImplementedError('abstract method')

    def _arguments_for_valid_syntax(
            self, path_to_check: str) -> TheInstructionArgumentsVariantConstructorForNotAndRelOpt:
        raise NotImplementedError('abstract method')

    def test_fail_WHEN_file_does_not_exist(self):
        instruction_argument_constructor = self._arguments_for_valid_syntax('name-of-non-existing-file')

        self._checker.check_rel_opt_variants_with_same_result_for_every_expectation_type(
            instruction_argument_constructor,
            asrt_pfh.is_fail())

    def test_fail_WHEN_file_does_exist_but_is_not_a_directory(self):
        name_of_regular_file = 'name-of-existing-regular-file'

        instruction_argument_constructor = self._arguments_for_valid_syntax(name_of_regular_file)

        self._checker.check_rel_opt_variants_with_same_result_for_every_expectation_type(
            instruction_argument_constructor,
            asrt_pfh.is_fail(),
            contents_of_relativity_option_root=DirContents([empty_file(name_of_regular_file)]))

    def test_fail_WHEN_file_is_a_sym_link_to_a_non_existing_file(self):
        broken_sym_link = sym_link('broken-sym-link', 'non-existing-file')

        instruction_argument_constructor = self._arguments_for_valid_syntax(broken_sym_link.name)

        contents_of_relativity_option_root = DirContents([broken_sym_link])

        self._checker.check_rel_opt_variants_with_same_result_for_every_expectation_type(
            instruction_argument_constructor,
            asrt_pfh.is_fail(),
            contents_of_relativity_option_root=contents_of_relativity_option_root)


def instruction_arguments_for_emptiness_check(rel_opt: RelativityOptionConfiguration,
                                              file_name: str) -> str:
    return '{relativity_option} {file_name} {emptiness_assertion_argument}'.format(
        relativity_option=rel_opt.option_string,
        file_name=file_name,
        emptiness_assertion_argument=EMPTINESS_CHECK_ARGUMENT)


EXPECTED_ACCEPTED_PATH_RELATIVITY_VARIANTS = PathRelativityVariants(
    {RelOptionType.REL_CWD,
     RelOptionType.REL_HOME_ACT,
     RelOptionType.REL_ACT,
     RelOptionType.REL_TMP},
    True)

ACCEPTED_REL_OPT_CONFIGURATIONS = (
    list(map(rel_opt_conf.conf_rel_any, EXPECTED_ACCEPTED_PATH_RELATIVITY_VARIANTS.rel_option_types)) +

    [rel_opt_conf.symbol_conf_rel_any(RelOptionType.REL_TMP,
                                      'symbol_name',
                                      EXPECTED_ACCEPTED_PATH_RELATIVITY_VARIANTS)] +

    [rel_opt_conf.default_conf_rel_any(RelOptionType.REL_CWD)]
)

UNACCEPTED_REL_OPT_CONFIGURATIONS = [
    rel_opt_conf.conf_rel_home(RelHomeOptionType.REL_HOME_CASE),
    rel_opt_conf.conf_rel_sds(RelSdsOptionType.REL_RESULT),
]

MAKE_CWD_OUTSIDE_OF_EVERY_REL_OPT_DIR = MkSubDirAndMakeItCurrentDirectory(
    SdsSubDirResolverFromSdsFun(lambda sds: sds.root_dir / 'test-cwd'))
