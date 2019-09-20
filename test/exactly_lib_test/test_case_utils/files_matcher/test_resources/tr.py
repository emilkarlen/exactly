import unittest
from abc import ABC

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.logic.files_matcher import FilesMatcherResolver
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher as sut
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.file_matcher import is_file_matcher_reference_to
from exactly_lib_test.test_case_file_structure.test_resources.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import \
    FilesMatcherArgumentsSetup
from exactly_lib_test.test_case_utils.files_matcher.test_resources.check_with_neg_and_rel_opts import MatcherChecker
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    pfh_expectation_type_config
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_actions import \
    MkSubDirAndMakeItCurrentDirectory
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class TestCaseBaseForParser(unittest.TestCase):
    @property
    def checker(self) -> MatcherChecker:
        return MatcherChecker(
            self,
            sut.files_matcher_parser())


class TestWithAssertionVariantBase(TestCaseBaseForParser):
    @property
    def assertion_variant(self) -> FilesMatcherArgumentsSetup:
        raise NotImplementedError('abstract method')


class TestParseInvalidSyntaxBase(TestWithAssertionVariantBase, ABC):
    def test_raise_exception_WHEN_there_is_an_initial_illegal_option(self):
        valid_instruction_arguments_con = args.complete_arguments_constructor(
            self.assertion_variant.arguments
        )
        parser = sut.files_matcher_parser()
        for expectation_type in ExpectationType:
            etc = pfh_expectation_type_config(expectation_type)
            valid_instruction_arguments = valid_instruction_arguments_con.apply(etc)
            instruction_args_with_invalid_initial_option = '{invalid_option} {valid_arguments}'.format(
                invalid_option=long_option_syntax('illegalOption'),
                valid_arguments=valid_instruction_arguments,
            )
            with self.subTest(arguments=instruction_args_with_invalid_initial_option,
                              expectation_type=str(expectation_type)):
                for source in equivalent_source_variants(self, instruction_args_with_invalid_initial_option):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(source)


class TestParseInvalidSyntaxWithMissingSelectorArgCaseBase(TestParseInvalidSyntaxBase, ABC):
    def test_raise_exception_WHEN_selector_option_argument_is_missing(self):
        instruction_args_without_valid_file_matcher = args.complete_arguments_constructor(
            self.assertion_variant.arguments,
            file_matcher=' '
        )
        parser = sut.files_matcher_parser()
        for expectation_type in ExpectationType:
            etc = pfh_expectation_type_config(expectation_type)
            instruction_arguments_without_valid_file_matcher_arg = instruction_args_without_valid_file_matcher.apply(
                etc)
            source = remaining_source(instruction_arguments_without_valid_file_matcher_arg)
            with self.subTest(arguments=instruction_arguments_without_valid_file_matcher_arg,
                              expectation_type=str(expectation_type)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class TestCommonSymbolReferencesBase(TestWithAssertionVariantBase):
    def test_file_matcher_reference_is_reported(self):
        name_of_file_matcher = 'a_file_matcher_symbol'

        arguments_constructor = args.complete_arguments_constructor(
            self.assertion_variant.arguments,
            file_matcher=name_of_file_matcher
        )

        arguments = arguments_constructor.apply(pfh_expectation_type_config(ExpectationType.NEGATIVE))

        source = remaining_source(arguments)

        # ACT #

        matcher = sut.files_matcher_parser().parse(source)
        assert isinstance(matcher, FilesMatcherResolver)
        actual = matcher.references

        # ASSERT #

        expected_references = asrt.matches_sequence(
            [is_file_matcher_reference_to(name_of_file_matcher)] +
            list(self.assertion_variant.expected_references)
        )
        expected_references.apply_without_message(self, actual)
        asrt_source.is_at_end_of_line(1)


MAKE_CWD_OUTSIDE_OF_EVERY_REL_OPT_DIR = MkSubDirAndMakeItCurrentDirectory(
    SdsSubDirResolverFromSdsFun(lambda sds: sds.root_dir / 'test-cwd'))
