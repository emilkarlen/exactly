import unittest

from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.instructions.assert_.contents_of_dir import config
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelHomeOptionType, \
    PathRelativityVariants, RelOptionType
from exactly_lib.test_case_utils.parse import parse_relativity
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources.instruction_arguments import \
    CompleteArgumentsConstructor, AssertionVariantArgumentsConstructor, CommonArgumentsConstructor
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.check_with_neg_and_rel_opts import \
    InstructionChecker
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check as asrt_pfh
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import equivalent_source_variants
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.symbol.test_resources.file_matcher import is_file_matcher_reference_to
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, sym_link
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_actions import \
    MkSubDirAndMakeItCurrentDirectory
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class TestCaseBaseForParser(unittest.TestCase):
    @property
    def checker(self) -> InstructionChecker:
        return InstructionChecker(
            self,
            sut.parser.Parser(),
            ACCEPTED_REL_OPT_CONFIGURATIONS)


class TestWithAssertionVariantBase(TestCaseBaseForParser):
    @property
    def assertion_variant_without_symbol_references(self) -> AssertionVariantArgumentsConstructor:
        raise NotImplementedError('abstract method')


class TestParseInvalidSyntaxBase(TestWithAssertionVariantBase):
    def test_raise_exception_WHEN_selector_option_argument_is_missing(self):
        instruction_args_without_valid_file_matcher = CompleteArgumentsConstructor(
            CommonArgumentsConstructor('file-name', file_matcher=' '),
            self.assertion_variant_without_symbol_references)
        parser = sut.parser.Parser()
        for rel_opt_config in [DEFAULT_REL_OPT_CONFIG,
                               ARBITRARY_ACCEPTED_REL_OPT_CONFIG]:
            for expectation_type in ExpectationType:
                etc = ExpectationTypeConfig(expectation_type)
                instruction_arguments_without_valid_file_matcher_arg = instruction_args_without_valid_file_matcher.apply(
                    etc, rel_opt_config)
                with self.subTest(arguments=instruction_arguments_without_valid_file_matcher_arg,
                                  expectation_type=str(expectation_type)):
                    for source in equivalent_source_variants(self,
                                                             instruction_arguments_without_valid_file_matcher_arg):
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            parser.parse(source)

    def test_raise_exception_WHEN_there_are_superfluous_arguments(self):
        valid_instruction_arguments_con = CompleteArgumentsConstructor(CommonArgumentsConstructor('file-name'),
                                                                       self.assertion_variant_without_symbol_references)
        parser = sut.parser.Parser()
        for rel_opt_config in [DEFAULT_REL_OPT_CONFIG,
                               ARBITRARY_ACCEPTED_REL_OPT_CONFIG]:
            for expectation_type in ExpectationType:
                etc = ExpectationTypeConfig(expectation_type)
                valid_instruction_arguments = valid_instruction_arguments_con.apply(etc, rel_opt_config)
                instruction_args_with_superfluous_arguments = '{valid_arguments} superfluous'.format(
                    valid_arguments=valid_instruction_arguments,
                )
                with self.subTest(arguments=instruction_args_with_superfluous_arguments,
                                  expectation_type=str(expectation_type)):
                    for source in equivalent_source_variants(self, instruction_args_with_superfluous_arguments):
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            parser.parse(source)

    def test_raise_exception_WHEN_there_is_an_initial_illegal_option(self):
        valid_instruction_arguments_con = CompleteArgumentsConstructor(CommonArgumentsConstructor('file-name'),
                                                                       self.assertion_variant_without_symbol_references)
        parser = sut.parser.Parser()
        for rel_opt_config in [DEFAULT_REL_OPT_CONFIG,
                               ARBITRARY_ACCEPTED_REL_OPT_CONFIG]:
            for expectation_type in ExpectationType:
                etc = ExpectationTypeConfig(expectation_type)
                valid_instruction_arguments = valid_instruction_arguments_con.apply(etc, rel_opt_config)
                instruction_args_with_invalid_initial_option = '{invalid_option} {valid_arguments}'.format(
                    invalid_option=long_option_syntax('illegalOption'),
                    valid_arguments=valid_instruction_arguments,
                )
                with self.subTest(arguments=instruction_args_with_invalid_initial_option,
                                  expectation_type=str(expectation_type)):
                    for source in equivalent_source_variants(self, instruction_args_with_invalid_initial_option):
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            parser.parse(source)

    def test_raise_exception_WHEN_relativity_is_unaccepted(self):
        valid_instruction_argument_syntax_con = CompleteArgumentsConstructor(CommonArgumentsConstructor('file-name'),
                                                                             self.assertion_variant_without_symbol_references)
        parser = sut.parser.Parser()
        for rel_opt_config in UNACCEPTED_REL_OPT_CONFIGURATIONS:
            for expectation_type in ExpectationType:
                etc = ExpectationTypeConfig(expectation_type)
                first_line_arguments = valid_instruction_argument_syntax_con.apply(etc, rel_opt_config)
                with self.subTest(arguments=first_line_arguments,
                                  expectation_type=str(expectation_type)):
                    for source in equivalent_source_variants(self, first_line_arguments):
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            parser.parse(source)


class TestCommonFailureConditionsBase(TestWithAssertionVariantBase):
    @property
    def _checker(self) -> InstructionChecker:
        return InstructionChecker(
            self,
            sut.parser.Parser(),
            ACCEPTED_REL_OPT_CONFIGURATIONS,
        )

    def test_fail_WHEN_file_does_not_exist(self):
        instruction_argument_constructor = CompleteArgumentsConstructor(
            CommonArgumentsConstructor('name-of-non-existing-file'),
            self.assertion_variant_without_symbol_references)

        self._checker.check_rel_opt_variants_with_same_result_for_every_expectation_type(
            instruction_argument_constructor,
            asrt_pfh.is_fail())

    def test_fail_WHEN_file_does_exist_but_is_not_a_directory(self):
        name_of_regular_file = 'name-of-existing-regular-file'

        instruction_argument_constructor = CompleteArgumentsConstructor(
            CommonArgumentsConstructor(name_of_regular_file),
            self.assertion_variant_without_symbol_references)

        self._checker.check_rel_opt_variants_with_same_result_for_every_expectation_type(
            instruction_argument_constructor,
            asrt_pfh.is_fail(),
            contents_of_relativity_option_root=DirContents([empty_file(name_of_regular_file)]))

    def test_fail_WHEN_file_is_a_sym_link_to_a_non_existing_file(self):
        broken_sym_link = sym_link('broken-sym-link', 'non-existing-file')

        instruction_argument_constructor = CompleteArgumentsConstructor(
            CommonArgumentsConstructor(broken_sym_link.name),
            self.assertion_variant_without_symbol_references)

        contents_of_relativity_option_root = DirContents([broken_sym_link])

        self._checker.check_rel_opt_variants_with_same_result_for_every_expectation_type(
            instruction_argument_constructor,
            asrt_pfh.is_fail(),
            contents_of_relativity_option_root=contents_of_relativity_option_root)


class TestCommonSymbolReferencesBase(TestWithAssertionVariantBase):
    def test_file_matcher_reference_is_reported(self):
        name_of_file_matcher = 'a_file_matcher_symbol'

        arguments_constructor = CompleteArgumentsConstructor(
            CommonArgumentsConstructor('ignored-dir-path',
                                       file_matcher=name_of_file_matcher),
            self.assertion_variant_without_symbol_references)

        arguments = arguments_constructor.apply(ExpectationTypeConfig(ExpectationType.NEGATIVE),
                                                DEFAULT_REL_OPT_CONFIG)

        source = remaining_source(arguments)

        # ACT #

        instruction = sut.parser.Parser().parse(source)
        assert isinstance(instruction, AssertPhaseInstruction)
        actual = instruction.symbol_usages()

        # ASSERT #

        expected_references = asrt.matches_sequence([
            is_file_matcher_reference_to(name_of_file_matcher)
        ])
        expected_references.apply_without_message(self, actual)

    def test_symbols_from_path_SHOULD_be_reported(self):
        # ARRANGE #

        path_sym_ref = SymbolReference(
            'path_symbol_name',
            parse_relativity.reference_restrictions_for_path_symbol(
                config.ACTUAL_RELATIVITY_CONFIGURATION.options.accepted_relativity_variants))

        arguments_constructor = CompleteArgumentsConstructor(
            CommonArgumentsConstructor('ignored-dir-path'),
            self.assertion_variant_without_symbol_references)

        rel_symbol_conf = rel_opt_conf.symbol_conf_rel_any(RelOptionType.REL_TMP,
                                                           path_sym_ref.name,
                                                           EXPECTED_ACCEPTED_PATH_RELATIVITY_VARIANTS)

        arguments = arguments_constructor.apply(ExpectationTypeConfig(ExpectationType.POSITIVE),
                                                rel_symbol_conf)

        source = remaining_source(arguments)

        # ACT #

        actual_instruction = sut.parser.Parser().parse(source)

        assert isinstance(actual_instruction, AssertPhaseInstruction)

        actual_symbol_references = actual_instruction.symbol_usages()

        # ASSERT #

        expected_symbol_references = [
            path_sym_ref,
        ]
        assertion = equals_symbol_references(expected_symbol_references)

        assertion.apply_without_message(self, actual_symbol_references)


EXPECTED_ACCEPTED_PATH_RELATIVITY_VARIANTS = PathRelativityVariants(
    {RelOptionType.REL_CWD,
     RelOptionType.REL_HOME_ACT,
     RelOptionType.REL_ACT,
     RelOptionType.REL_TMP},
    True)

DEFAULT_REL_OPT_CONFIG = rel_opt_conf.default_conf_rel_any(RelOptionType.REL_CWD)

ARBITRARY_ACCEPTED_REL_OPT_CONFIG = rel_opt_conf.conf_rel_any(RelOptionType.REL_TMP)

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
