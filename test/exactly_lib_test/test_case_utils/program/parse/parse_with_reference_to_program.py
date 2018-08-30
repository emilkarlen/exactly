import unittest
from typing import List, Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import file_ref_resolvers, list_resolvers, string_resolvers
from exactly_lib.symbol.data.file_ref_resolvers import constant
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RESOLVING_DEPENDENCY_OF
from exactly_lib.test_case_utils.program.command import arguments_resolvers
from exactly_lib.test_case_utils.program.parse import parse_with_reference_to_program as sut
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.file_refs import simple_of_rel_option
from exactly_lib.type_system.logic.program.program_value import Program
from exactly_lib.util.parse.token import QuoteType, QUOTE_CHAR_FOR_TYPE
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import program as asrt_pgm
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_file_structure.test_resources import dir_dep_value_assertions as asrt_dir_dep_val, \
    sds_populator
from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HomePopulator, SdsPopulator
from exactly_lib_test.test_case_utils.parse.test_resources import arguments_building as parse_args
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.program.test_resources import command_cmd_line_args as sym_ref_args
from exactly_lib_test.test_case_utils.program.test_resources import program_execution_check as pgm_exe_check
from exactly_lib_test.test_case_utils.program.test_resources import program_resolvers
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources import program_assertions as asrt_pgm_val
from exactly_lib_test.type_system.logic.test_resources import string_transformer_assertions as asrt_line_transformer
from exactly_lib_test.util.test_resources import command_assertions as asrt_command


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestSymbolReferences),
        unittest.makeSuite(TestValidation),
        unittest.makeSuite(TestResolving),
        unittest.makeSuite(TestExecution),
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
            NameAndValue('valid symbol name - broken argument syntax due to missing end quote',
                         sym_ref_args.sym_ref_cmd_line('valid_symbol_name',
                                                       [QUOTE_CHAR_FOR_TYPE[QuoteType.SOFT] + 'argument'])
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
                expected_value=
                asrt.matches_sequence([
                    asrt_pgm.is_program_reference_to(program_symbol_name),
                ]),
                input_value=
                sym_ref_args.sym_ref_cmd_line(program_symbol_name),
                ),
            NIE('single argument that is a reference to a symbol',
                expected_value=
                asrt.matches_sequence([
                    asrt_pgm.is_program_reference_to(program_symbol_name),
                    asrt_sym_ref.is_reference_to_data_type_symbol(argument_symbol_name),
                ]),
                input_value=
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


class TestExecution(unittest.TestCase):
    def test(self):
        # ARRANGE #

        parser = sut.program_parser()

        cases = [
            NameAndValue('0 exit code',
                         0),
            NameAndValue('72 exit code',
                         72),
        ]
        for case in cases:
            with self.subTest(case.name):
                python_source = 'exit({exit_code})'.format(exit_code=case.value)

                resolver_of_referred_program = program_resolvers.for_py_source_on_command_line(python_source)

                program_that_executes_py_source = NameAndValue(
                    'PROGRAM_THAT_EXECUTES_PY_SOURCE',
                    resolver_of_referred_program
                )

                source = parse_source_of(sym_ref_args.sym_ref_cmd_line(
                    program_that_executes_py_source.name))

                symbols = SymbolTable({
                    program_that_executes_py_source.name:
                        symbol_utils.container(program_that_executes_py_source.value)
                })

                # ACT & ASSERT #
                pgm_exe_check.check(self,
                                    parser,
                                    source,
                                    pgm_exe_check.Arrangement(
                                        symbols=symbols),
                                    pgm_exe_check.Expectation(
                                        symbol_references=asrt.matches_sequence([
                                            asrt_pgm.is_program_reference_to(program_that_executes_py_source.name),
                                        ]),
                                        result=pgm_exe_check.assert_process_result_data(
                                            exitcode=asrt.equals(case.value),
                                            stdout_contents=asrt.equals(''),
                                            stderr_contents=asrt.equals(''),
                                            contents_after_transformation=asrt.equals(''),
                                        )
                                    ))


class ResolvingCase:
    def __init__(self,
                 name: str,
                 actual_resolver: ProgramResolver,
                 expected: asrt.ValueAssertion[DirDependentValue[Program]]):
        self.name = name
        self.actual_resolver = actual_resolver
        self.expected = expected


class TestResolving(unittest.TestCase):
    @staticmethod
    def _executable_file_case(expected_arguments: List[str]) -> Sequence[ResolvingCase]:
        file_name = 'the exe file'

        def case(relativity: RelOptionType) -> ResolvingCase:
            exe_file_ref = file_refs.of_rel_option(relativity, file_refs.constant_path_part(file_name))

            def assertion(tcds: HomeAndSds) -> asrt.ValueAssertion[Program]:
                return asrt_pgm_val.matches_program(
                    command=asrt_command.equals_executable_file_command(
                        executable_file=exe_file_ref.value_of_any_dependency(tcds),
                        arguments=expected_arguments
                    ),
                    stdin=asrt_pgm_val.no_stdin(),
                    transformer=asrt_line_transformer.is_identity_transformer()
                )

            return ResolvingCase('relativity=' + str(relativity),
                                 actual_resolver=program_resolvers.with_ref_to_exe_file(
                                     file_ref_resolvers.constant(exe_file_ref),
                                     arguments_resolvers.new_without_validation(
                                         list_resolvers.from_str_constants(expected_arguments))),
                                 expected=asrt_dir_dep_val.matches_dir_dependent_value(
                                     asrt.equals({RESOLVING_DEPENDENCY_OF[relativity]}), assertion))

        return [case(RelOptionType.REL_HOME_ACT),
                case(RelOptionType.REL_TMP)]

    @staticmethod
    def _executable_program_case(expected_arguments: List[str]
                                 ) -> Sequence[ResolvingCase]:
        the_executable_program = 'the executable program'

        def assertion(tcds: HomeAndSds) -> asrt.ValueAssertion[Program]:
            return asrt_pgm_val.matches_program(
                command=asrt_command.equals_system_program_command(
                    program=the_executable_program,
                    arguments=expected_arguments
                ),
                stdin=asrt_pgm_val.no_stdin(),
                transformer=asrt_line_transformer.is_identity_transformer()
            )

        case = ResolvingCase('', actual_resolver=program_resolvers.with_ref_to_program(
            string_resolvers.str_constant(the_executable_program),
            arguments_resolvers.new_without_validation(list_resolvers.from_str_constants(expected_arguments))),
                             expected=asrt_dir_dep_val.matches_dir_dependent_value(asrt.equals(set()), assertion))
        return [case]

    def test(self):
        # ARRANGE #

        parser = sut.program_parser()

        argument_cases = [
            NameAndValue('no arguments', []
                         ),
            NameAndValue('single arguments', ['an argument']
                         ),
        ]

        program_cases = [
            NameAndValue('executable file', self._executable_file_case),
            NameAndValue('executable program', self._executable_program_case),
        ]

        for argument_case in argument_cases:
            for program_case in program_cases:
                for resolving_case in program_case.value(argument_case.value):
                    with self.subTest(program=program_case.name,
                                      arguments=argument_case.name,
                                      resolving_case=resolving_case.name):
                        program_symbol = NameAndValue(
                            'PROGRAM_SYMBOL',
                            resolving_case.actual_resolver)

                        source = parse_source_of(sym_ref_args.sym_ref_cmd_line(program_symbol.name))

                        symbols = SymbolTable({
                            program_symbol.name:
                                symbol_utils.container(program_symbol.value)
                        })

                        expected_references_assertion = asrt.matches_sequence([
                            asrt_pgm.is_program_reference_to(program_symbol.name),
                        ])

                        # ACT #

                        actual = parser.parse(source)

                        # ASSERT #

                        actual_references = actual.references

                        expected_references_assertion.apply_with_message(self,
                                                                         actual_references,
                                                                         'references')
                        actual_resolved_value = actual.resolve(symbols)

                        resolving_case.expected.apply_with_message(self,
                                                                   actual_resolved_value,
                                                                   'resolved value')


def parse_source_of(single_line: ArgumentElementRenderer) -> ParseSource:
    return ArgumentElements([single_line]).as_remaining_source


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
