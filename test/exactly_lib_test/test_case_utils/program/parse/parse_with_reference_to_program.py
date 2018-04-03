import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.file_ref_resolvers2 import constant
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.program.parse import parse_with_reference_to_program as sut
from exactly_lib.type_system.data.file_refs import simple_of_rel_option
from exactly_lib.util.parse.token import QuoteType, QUOTE_CHAR_FOR_TYPE
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.data.restrictions.test_resources import concrete_restriction_assertion as asrt_rr
from exactly_lib_test.symbol.test_resources import program as asrt_pgm
from exactly_lib_test.symbol.test_resources import resolver_structure_assertions as asrt_sym
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HomePopulator, SdsPopulator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_utils.parse.test_resources import arguments_building as parse_args
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.program.test_resources import program_resolvers
from exactly_lib_test.test_case_utils.program.test_resources import sym_ref_cmd_line_args as sym_ref_args
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestSymbolReferences),
    ])


class TestFailingParse(unittest.TestCase):
    def test(self):
        # ARRANGE #
        cases = [
            NameAndValue('empty source',
                         parse_args.empty()
                         ),
            NameAndValue('not a plain symbol name - quoted - hard',
                         sym_ref_args.sym_ref_cmd_line(ab.quoted_string('valid_symbol_name', QuoteType.HARD))
                         ),
            NameAndValue('not a plain symbol name - quoted - soft',
                         sym_ref_args.sym_ref_cmd_line(ab.quoted_string('valid_symbol_name', QuoteType.SOFT))
                         ),
            NameAndValue('not a plain symbol name - symbol reference',
                         sym_ref_args.sym_ref_cmd_line(ab.symbol_reference('valid_symbol_name'))
                         ),
            NameAndValue('not a plain symbol name - broken syntax due to missing end quote',
                         sym_ref_args.sym_ref_cmd_line(QUOTE_CHAR_FOR_TYPE[QuoteType.SOFT] + 'valid_symbol_name')
                         ),
        ]
        parser = sut.program_parser()
        for case in cases:
            source = parse_source_of(case.value)
            with self.subTest(case.name):
                # ASSERT #
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT #
                    parser.parse(source)


class TestSymbolReferences(unittest.TestCase):
    def test(self):
        parser = sut.program_parser()

        program_symbol_name = 'PROGRAM_SYMBOL'
        argument_symbol_name = 'ARGUMENT_SYMBOL'

        cases = [
            NIE('just program reference symbol',
                asrt.matches_sequence([
                    asrt_pgm.is_program_reference_to(program_symbol_name),
                ]),
                sym_ref_args.sym_ref_cmd_line(program_symbol_name),
                ),
            NIE('single argument that is a reference to a symbol',
                asrt.matches_sequence([
                    asrt_pgm.is_program_reference_to(program_symbol_name),
                    is_reference_data_type_symbol(argument_symbol_name),
                ]),
                sym_ref_args.sym_ref_cmd_line(program_symbol_name, [ab.symbol_reference(argument_symbol_name)]),
                ),
        ]
        for case in cases:
            source = parse_source_of(case.input_value)
            assertion = case.expected_value
            assert isinstance(assertion, asrt.ValueAssertion)  # Type info for IDE

            with self.subTest(case.name):
                # ACT #
                actual = parser.parse(source)
                # ASSERT #
                self.assertIsInstance(actual, ProgramResolver)
                assertion.apply_without_message(self, actual.references)


class ValidationPreSdsCase:
    def __init__(self,
                 name: str,
                 source: ArgumentElementRenderer,
                 home_contents: HomePopulator,
                 ):
        self.name = name
        self.source = source
        self.home_contents = home_contents


class ValidationPostSdsCase:
    def __init__(self,
                 name: str,
                 source: ArgumentElementRenderer,
                 sds_contents: SdsPopulator,
                 ):
        self.name = name
        self.source = source
        self.sds_contents = sds_contents


class TestValidation(unittest.TestCase):
    def test_failing_validation_pre_sds(self):
        parser = sut.program_parser()

        program_symbol_with_ref_to_non_exit_exe_file = NameAndValue(
            'PGM_WITH_REF_TO_EXE_FILE',
            program_resolvers.with_ref_to_exe_file(constant(simple_of_rel_option(RelOptionType.REL_HOME_ACT,
                                                                                 'non-existing-exe-file')))
        )

        program_symbol_with_ref_to_non_exiting_file_as_argument = NameAndValue(
            'PGM_WITH_REF_TO_SOURCE_FILE',
            program_resolvers.interpret_py_source_file_that_must_exist(
                constant(simple_of_rel_option(RelOptionType.REL_HOME_ACT,
                                              'non-existing-python-file.py')))
        )

        symbols = SymbolTable({
            program_symbol_with_ref_to_non_exit_exe_file.name:
                symbol_utils.container(program_symbol_with_ref_to_non_exit_exe_file.value),

            program_symbol_with_ref_to_non_exiting_file_as_argument.name:
                symbol_utils.container(program_symbol_with_ref_to_non_exiting_file_as_argument.value)
        })

        cases = [
            ValidationPreSdsCase('executable does not exist',
                                 sym_ref_args.sym_ref_cmd_line(program_symbol_with_ref_to_non_exit_exe_file.name),
                                 home_populators.empty()
                                 ),
            ValidationPreSdsCase('source file does not exist',
                                 sym_ref_args.sym_ref_cmd_line(
                                     program_symbol_with_ref_to_non_exiting_file_as_argument.name),
                                 home_populators.empty()
                                 ),
        ]

        for case in cases:
            source = parse_source_of(case.source)

            with self.subTest(case.name):
                # ACT #
                program_resolver = parser.parse(source)
                # ASSERT #
                self.assertIsInstance(program_resolver, ProgramResolver)
                with home_and_sds_with_act_as_curr_dir(hds_contents=case.home_contents,
                                                       symbols=symbols) as environment:
                    # ACT #
                    actual = program_resolver.validator.validate_pre_sds_if_applicable(environment)
                    # ASSERT #
                    self.assertIsNotNone(actual)
                    # ACT #
                    actual = program_resolver.validator.validate_post_sds_if_applicable(environment)
                    # ASSERT #
                    self.assertIsNone(actual)

    def test_failing_validation_post_sds(self):
        parser = sut.program_parser()

        program_symbol_with_ref_to_non_exit_exe_file = NameAndValue(
            'PGM_WITH_REF_TO_EXE_FILE',
            program_resolvers.with_ref_to_exe_file(constant(simple_of_rel_option(RelOptionType.REL_TMP,
                                                                                 'non-existing-exe-file')))
        )

        program_symbol_with_ref_to_non_exiting_file_as_argument = NameAndValue(
            'PGM_WITH_REF_TO_SOURCE_FILE',
            program_resolvers.interpret_py_source_file_that_must_exist(
                constant(simple_of_rel_option(RelOptionType.REL_ACT,
                                              'non-existing-python-file.py')))
        )

        symbols = SymbolTable({
            program_symbol_with_ref_to_non_exit_exe_file.name:
                symbol_utils.container(program_symbol_with_ref_to_non_exit_exe_file.value),

            program_symbol_with_ref_to_non_exiting_file_as_argument.name:
                symbol_utils.container(program_symbol_with_ref_to_non_exiting_file_as_argument.value)
        })

        cases = [
            ValidationPostSdsCase('executable does not exist',
                                  sym_ref_args.sym_ref_cmd_line(program_symbol_with_ref_to_non_exit_exe_file.name),
                                  sds_populator.empty()
                                  ),
            ValidationPostSdsCase('source file does not exist',
                                  sym_ref_args.sym_ref_cmd_line(
                                      program_symbol_with_ref_to_non_exiting_file_as_argument.name),
                                  sds_populator.empty()
                                  ),
        ]

        for case in cases:
            source = parse_source_of(case.source)

            with self.subTest(case.name):
                # ACT #
                program_resolver = parser.parse(source)
                # ASSERT #
                self.assertIsInstance(program_resolver, ProgramResolver)
                with home_and_sds_with_act_as_curr_dir(sds_contents=case.sds_contents,
                                                       symbols=symbols) as environment:
                    # ACT #
                    actual = program_resolver.validator.validate_pre_sds_if_applicable(environment)
                    # ASSERT #
                    self.assertIsNone(actual)
                    # ACT #
                    actual = program_resolver.validator.validate_post_sds_if_applicable(environment)
                    # ASSERT #
                    self.assertIsNotNone(actual)


def is_reference_data_type_symbol(symbol_name: str) -> asrt.ValueAssertion:
    return asrt_sym.matches_reference(asrt.equals(symbol_name),
                                      asrt_rr.is_any_data_type_reference_restrictions())


def parse_source_of(single_line: ArgumentElementRenderer) -> ParseSource:
    return ArgumentElements([single_line]).as_remaining_source


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
