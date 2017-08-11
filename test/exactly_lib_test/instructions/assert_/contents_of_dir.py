import unittest

from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelHomeOptionType, \
    PathRelativityVariants, RelOptionType
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import TestCaseBase, \
    Expectation
from exactly_lib_test.instructions.assert_.test_resources.instruction_check_with_not_and_rel_opts import \
    TestCaseBaseWithParser, InstructionArgumentsVariantConstructor
from exactly_lib_test.instructions.assert_.test_resources.instruction_with_negation_argument import \
    ExpectationTypeConfig, PassOrFail
from exactly_lib_test.instructions.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check as asrt_pfh
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, Dir, sym_link, \
    empty_dir_contents
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_actions import \
    MkSubDirAndMakeItCurrentDirectory
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),
        unittest.makeSuite(TestEmpty),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('the-instruction-name')),
    ])


class TheInstructionArgumentsVariantConstructor(InstructionArgumentsVariantConstructor):
    """
    Constructs the instruction argument for a given negation-option config
    and rel-opt config.
    """

    def apply(self,
              etc: ExpectationTypeConfig,
              rel_opt_config: RelativityOptionConfiguration,
              ) -> str:
        ret_val = self.instruction_argument_template.replace('<rel_opt>', rel_opt_config.option_string)
        ret_val = etc.instruction_arguments(ret_val)
        return ret_val


class TestCaseBaseForParser(TestCaseBaseWithParser):
    parser = sut.Parser()

    def _parser(self) -> InstructionParser:
        return self.parser

    def _accepted_rel_opt_configurations(self) -> list:
        return ACCEPTED_REL_OPT_CONFIGURATIONS

    def _run(self,
             instruction_argument: str,
             arrangement: ArrangementPostAct,
             expectation: Expectation):
        parser = sut.Parser()
        for source in equivalent_source_variants(self, instruction_argument):
            self._check(parser, source, arrangement, expectation)

    def _check_with_rel_opt_config(self,
                                   instruction_argument_str: str,
                                   rel_opt_config: RelativityOptionConfiguration,
                                   main_result: asrt.ValueAssertion,
                                   contents_of_relativity_option_root: DirContents = empty_dir_contents(),
                                   ):
        self._run(
            instruction_argument_str,
            ArrangementPostAct(
                pre_contents_population_action=MAKE_CWD_OUTSIDE_OF_EVERY_REL_OPT_DIR,
                home_or_sds_contents=rel_opt_config.populator_for_relativity_option_root(
                    contents_of_relativity_option_root
                ),
                symbols=rel_opt_config.symbols.in_arrangement(),
            ),
            Expectation(
                main_result=main_result,
                symbol_usages=rel_opt_config.symbols.usages_expectation(),
            ))


class TestParseInvalidSyntax(TestCaseBase):
    test_cases_with_no_negation_operator = [
        NameAndValue(
            'no arguments',
            '',
        ),
        NameAndValue(
            'valid file argument, but no operator',
            'file-name',
        ),
        NameAndValue(
            'valid file argument, invalid operator',
            'file-name invalid-operator',
        ),
        NameAndValue(
            'invalid option before file argument',
            '{invalid_option} file-name'.format(
                invalid_option=long_option_syntax('invalidOption'))
        ),
    ]

    def test_raise_exception_WHEN_syntax_is_invalid(self):

        self._assert_each_case_raises_SingleInstructionInvalidArgumentException(
            self.test_cases_with_no_negation_operator)

    def test_raise_exception_WHEN_relativity_is_unaccepted(self):

        test_cases = [
            NameAndValue('relativity:' + rel_opt_config.option_string,
                         instruction_arguments_for_emptiness_check(rel_opt_config,
                                                                   'file-name')
                         )
            for rel_opt_config in UNACCEPTED_REL_OPT_CONFIGURATIONS
        ]

        self._assert_each_case_raises_SingleInstructionInvalidArgumentException(test_cases)

    def _assert_each_case_raises_SingleInstructionInvalidArgumentException(self, test_cases: list):
        parser = sut.Parser()
        for name_and_instruction_argument_str in test_cases:
            with self.subTest(case_name=name_and_instruction_argument_str.name):
                for source in equivalent_source_variants(self, name_and_instruction_argument_str.value):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(source)


class TestEmpty(TestCaseBaseForParser):
    def test_fail_WHEN_file_does_not_exist(self):
        instruction_argument_constructor = argument_constructor_for_emptiness_check('name-of-non-existing-file')

        self._check_with_rel_opt_variants_and_same_result_for_all_expectation_types(
            instruction_argument_constructor,
            asrt_pfh.is_fail())

    def test_fail_WHEN_file_does_exist_but_is_not_a_directory(self):
        name_of_regular_file = 'name-of-existing-regular-file'
        instruction_argument_constructor = argument_constructor_for_emptiness_check(name_of_regular_file)

        self._check_with_rel_opt_variants_and_same_result_for_all_expectation_types(
            instruction_argument_constructor,
            asrt_pfh.is_fail(),
            contents_of_relativity_option_root=DirContents([empty_file(name_of_regular_file)]))

    def test_fail_WHEN_file_is_a_sym_link_to_a_non_existing_file(self):
        broken_sym_link = sym_link('broken-sym-link', 'non-existing-file')
        instruction_argument_constructor = argument_constructor_for_emptiness_check(broken_sym_link.name)
        contents_of_relativity_option_root = DirContents([broken_sym_link])

        self._check_with_rel_opt_variants_and_same_result_for_all_expectation_types(
            instruction_argument_constructor,
            asrt_pfh.is_fail(),
            contents_of_relativity_option_root=contents_of_relativity_option_root)

    def test_file_is_an_directory_BUT_is_not_empty(self):
        name_of_directory = 'name-of-empty_directory'
        instruction_argument_constructor = argument_constructor_for_emptiness_check(name_of_directory)

        contents_of_relativity_option_root = DirContents([Dir(name_of_directory, [
            empty_file('existing-file-in-checked-dir')
        ])])

        self._check_with_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.FAIL,
            contents_of_relativity_option_root=contents_of_relativity_option_root)

    def test_file_is_an_empty_directory(self):
        name_of_empty_directory = 'name-of-empty_directory'
        instruction_argument_constructor = argument_constructor_for_emptiness_check(name_of_empty_directory)

        contents_of_relativity_option_root = DirContents([empty_dir(name_of_empty_directory)])

        self._check_with_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root)

    def test_file_is_a_symbolic_link_to_an_empty_directory(self):
        name_of_empty_directory = 'name-of-empty_directory'
        name_of_symbolic_link = 'link-to-empty_directory'

        instruction_argument_constructor = argument_constructor_for_emptiness_check(name_of_symbolic_link)

        contents_of_relativity_option_root = DirContents([empty_dir(name_of_empty_directory),
                                                          sym_link(name_of_symbolic_link,
                                                                   name_of_empty_directory)])

        self._check_with_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root)


def instruction_arguments_for_emptiness_check(rel_opt: RelativityOptionConfiguration,
                                              file_name: str) -> str:
    return '{relativity_option} {file_name} {emptiness_assertion_argument}'.format(
        relativity_option=rel_opt.option_string,
        file_name=file_name,
        emptiness_assertion_argument=EMPTINESS_CHECK_ARGUMENT)


def argument_constructor_for_emptiness_check(file_name: str) -> TheInstructionArgumentsVariantConstructor:
    return TheInstructionArgumentsVariantConstructor(
        '<rel_opt> {file_name} {empty}'.format(
            file_name=file_name,
            empty=EMPTINESS_CHECK_ARGUMENT,
        )
    )


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

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
