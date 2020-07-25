import unittest
from typing import List, Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import path_sdvs, list_sdvs, string_sdvs
from exactly_lib.symbol.data.path_sdvs import constant
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.program.command import arguments_sdvs
from exactly_lib.test_case_utils.program.parse import parse_with_reference_to_program as sut
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.paths import simple_of_rel_option
from exactly_lib.type_system.logic.program.program import Program, ProgramAdv
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType, QUOTE_CHAR_FOR_TYPE
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.symbol.data.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources import program as asrt_pgm
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.test_resources import command_assertions as asrt_command
from exactly_lib_test.test_case_file_structure.test_resources import dir_dep_value_assertions as asrt_dir_dep_val, \
    sds_populator
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators
from exactly_lib_test.test_case_file_structure.test_resources.application_environment import \
    application_environment_for_test
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HdsPopulator, SdsPopulator
from exactly_lib_test.test_case_file_structure.test_resources.ds_construction import tcds_with_act_as_curr_dir_2
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Expectation, ParseExpectation, \
    arrangement_w_tcds, ExecutionExpectation
from exactly_lib_test.test_case_utils.parse.test_resources import arguments_building as parse_args
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.program.test_resources import command_cmd_line_args as sym_ref_args, \
    program_checker
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.program.test_resources.assertions import assert_process_result_data
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_case_utils.test_resources import pre_or_post_sds_validator
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer
from exactly_lib_test.test_resources.programs.py_programs import py_pgm_with_stdout_stderr_exit_code
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.string_transformer.test_resources import \
    string_transformer_assertions as asrt_line_transformer
from exactly_lib_test.type_system.logic.test_resources import program_assertions as asrt_pgm_val


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
            with self.subTest(case=case.name):
                # ASSERT #
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT #
                    parser.parse(source)


class TestSymbolReferences(unittest.TestCase):
    def test(self):
        program_symbol_name = 'PROGRAM_SYMBOL'
        argument_symbol_name = 'ARGUMENT_SYMBOL'

        cases = [
            NIE('just program reference symbol',
                expected_value=
                asrt.matches_sequence([
                    asrt_pgm.is_reference_to_program(program_symbol_name),
                ]),
                input_value=
                sym_ref_args.sym_ref_cmd_line(program_symbol_name),
                ),
            NIE('single argument that is a reference to a symbol',
                expected_value=
                asrt.matches_sequence([
                    asrt_pgm.is_reference_to_program(program_symbol_name),
                    asrt_sym_ref.is_reference_to_data_type_symbol(argument_symbol_name),
                ]),
                input_value=
                sym_ref_args.sym_ref_cmd_line(program_symbol_name, [ab.symbol_reference(argument_symbol_name)]),
                ),
        ]
        parser = sut.program_parser()
        for case in cases:
            source = parse_source_of(case.input_value)
            assertion = case.expected_value
            assert isinstance(assertion, ValueAssertion)  # Type info for IDE

            with self.subTest(case=case.name):
                # ACT #
                actual = parser.parse(source)
                # ASSERT #
                self.assertIsInstance(actual, ProgramSdv)
                assertion.apply_without_message(self, actual.references)


class ValidationPreSdsCase:
    def __init__(self,
                 name: str,
                 source: ArgumentElementsRenderer,
                 home_contents: HdsPopulator,
                 ):
        self.name = name
        self.source = source
        self.home_contents = home_contents


class ValidationPostSdsCase:
    def __init__(self,
                 name: str,
                 source: ArgumentElementsRenderer,
                 sds_contents: SdsPopulator,
                 ):
        self.name = name
        self.source = source
        self.sds_contents = sds_contents


class TestValidation(unittest.TestCase):
    def test_failing_validation_pre_sds(self):
        expected_validation = validation.pre_sds_validation_fails__w_any_msg()

        program_symbol_with_ref_to_non_exit_exe_file = ProgramSymbolContext.of_sdv(
            'PGM_WITH_REF_TO_EXE_FILE',
            program_sdvs.ref_to_exe_file(constant(simple_of_rel_option(RelOptionType.REL_HDS_ACT,
                                                                       'non-existing-exe-file')))
        )

        program_symbol_with_ref_to_non_exiting_file_as_argument = ProgramSymbolContext.of_sdv(
            'PGM_WITH_REF_TO_SOURCE_FILE',
            program_sdvs.interpret_py_source_file_that_must_exist(
                constant(simple_of_rel_option(RelOptionType.REL_HDS_ACT,
                                              'non-existing-python-file.py')))
        )

        symbols = SymbolContext.symbol_table_of_contexts([
            program_symbol_with_ref_to_non_exit_exe_file,
            program_symbol_with_ref_to_non_exiting_file_as_argument,
        ])

        cases = [
            ValidationPreSdsCase('executable does not exist',
                                 sym_ref_args.sym_ref_cmd_line(program_symbol_with_ref_to_non_exit_exe_file.name),
                                 hds_populators.empty()
                                 ),
            ValidationPreSdsCase('source file does not exist',
                                 sym_ref_args.sym_ref_cmd_line(
                                     program_symbol_with_ref_to_non_exiting_file_as_argument.name),
                                 hds_populators.empty()
                                 ),
        ]

        parser = sut.program_parser()
        for case in cases:
            source = parse_source_of(case.source)

            with self.subTest(case=case.name):
                # ACT #
                program_sdv = parser.parse(source)
                validator = program_sdv.resolve(symbols).validator
                # ASSERT #
                self.assertIsInstance(program_sdv, ProgramSdv)
                with tcds_with_act_as_curr_dir_2(hds_contents=case.home_contents) as tcds:
                    validation_assertion = pre_or_post_sds_validator.PreOrPostSdsDdvValidationAssertion(
                        tcds,
                        expected_validation,
                    )
                    validation_assertion.apply_without_message(self, validator)

    def test_failing_validation_post_sds(self):
        expected_validation = validation.post_sds_validation_fails__w_any_msg()

        program_symbol_with_ref_to_non_exit_exe_file = ProgramSymbolContext.of_sdv(
            'PGM_WITH_REF_TO_EXE_FILE',
            program_sdvs.ref_to_exe_file(constant(simple_of_rel_option(RelOptionType.REL_TMP,
                                                                       'non-existing-exe-file')))
        )

        program_symbol_with_ref_to_non_exiting_file_as_argument = ProgramSymbolContext.of_sdv(
            'PGM_WITH_REF_TO_SOURCE_FILE',
            program_sdvs.interpret_py_source_file_that_must_exist(
                constant(simple_of_rel_option(RelOptionType.REL_ACT,
                                              'non-existing-python-file.py')))
        )

        symbols = SymbolContext.symbol_table_of_contexts([
            program_symbol_with_ref_to_non_exit_exe_file,
            program_symbol_with_ref_to_non_exiting_file_as_argument,
        ])

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

        parser = sut.program_parser()

        for case in cases:
            source = parse_source_of(case.source)

            with self.subTest(case=case.name):
                # ACT #
                program_sdv = parser.parse(source)
                validator = program_sdv.resolve(symbols).validator
                # ASSERT #
                self.assertIsInstance(program_sdv, ProgramSdv)
                with tcds_with_act_as_curr_dir_2(sds_contents=case.sds_contents) as tcds:
                    validation_assertion = pre_or_post_sds_validator.PreOrPostSdsDdvValidationAssertion(
                        tcds,
                        expected_validation,
                    )
                    validation_assertion.apply_without_message(self, validator)


class TestExecution(unittest.TestCase):
    def test(self):
        # ARRANGE #

        stdout_contents = 'output on stdout'
        stderr_contents = 'output on stderr'

        exit_code_cases = [0, 72]

        transformation_cases = [
            NIE(
                'stdout',
                stdout_contents,
                ProcOutputFile.STDOUT,
            ),
            NIE(
                'stderr',
                stderr_contents,
                ProcOutputFile.STDERR,
            ),
        ]
        for exit_code_case in exit_code_cases:
            for transformation_case in transformation_cases:
                with self.subTest(
                        exit_code=exit_code_case,
                        transformation=transformation_case.name):
                    python_source = py_pgm_with_stdout_stderr_exit_code(stdout_contents,
                                                                        stderr_contents,
                                                                        exit_code_case)

                    sdv_of_referred_program = program_sdvs.for_py_source_on_command_line(python_source)

                    program_that_executes_py_source = ProgramSymbolContext.of_sdv(
                        'PROGRAM_THAT_EXECUTES_PY_SOURCE',
                        sdv_of_referred_program
                    )

                    source = parse_source_of(sym_ref_args.sym_ref_cmd_line(
                        program_that_executes_py_source.name))

                    symbols = program_that_executes_py_source.symbol_table

                    # ACT & ASSERT #
                    _INTEGRATION_CHECKER.check(
                        self,
                        source,
                        transformation_case.input_value,
                        arrangement_w_tcds(
                            symbols=symbols,
                        ),
                        Expectation(
                            ParseExpectation(
                                symbol_references=asrt.matches_sequence([
                                    program_that_executes_py_source.reference_assertion,
                                ]),
                            ),
                            ExecutionExpectation(
                                main_result=assert_process_result_data(
                                    exitcode=asrt.equals(exit_code_case),
                                    stdout_contents=asrt.equals(stdout_contents),
                                    stderr_contents=asrt.equals(stderr_contents),
                                    contents_after_transformation=asrt.equals(transformation_case.expected_value),
                                )
                            )
                        )
                    )


class ResolvingCase:
    def __init__(self,
                 name: str,
                 actual_sdv: ProgramSdv,
                 expected: ValueAssertion[DirDependentValue[ProgramAdv]]):
        self.name = name
        self.actual_sdv = actual_sdv
        self.expected = expected


class TestResolving(unittest.TestCase):
    @staticmethod
    def _executable_file_case(expected_arguments: List[str]) -> Sequence[ResolvingCase]:
        file_name = 'the exe file'

        def case(relativity: RelOptionType) -> ResolvingCase:
            exe_path = paths.of_rel_option(relativity, paths.constant_path_part(file_name))

            def program_assertion(tcds: Tcds) -> ValueAssertion[Program]:
                return asrt_pgm_val.matches_program(
                    command=asrt_command.equals_executable_file_command(
                        executable_file=exe_path.value_of_any_dependency__d(tcds),
                        arguments=expected_arguments
                    ),
                    stdin=asrt_pgm_val.no_stdin(),
                    transformer=asrt_line_transformer.is_identity_transformer(True)
                )

            def program_adv_assertion(tcds: Tcds) -> ValueAssertion[ProgramAdv]:
                def get_program(adv: ProgramAdv) -> Program:
                    return adv.primitive(application_environment_for_test())

                return asrt.is_instance_with(ProgramAdv,
                                             asrt.sub_component('program',
                                                                get_program,
                                                                program_assertion(tcds)))

            return ResolvingCase('relativity=' + str(relativity),
                                 actual_sdv=program_sdvs.ref_to_exe_file(
                                     path_sdvs.constant(exe_path),
                                     arguments_sdvs.new_without_validation(
                                         list_sdvs.from_str_constants(expected_arguments))),
                                 expected=asrt_dir_dep_val.matches_dir_dependent_value(program_adv_assertion))

        return [case(RelOptionType.REL_HDS_ACT),
                case(RelOptionType.REL_TMP)]

    @staticmethod
    def _executable_program_case(expected_arguments: List[str]
                                 ) -> Sequence[ResolvingCase]:
        the_executable_program = 'the executable program'

        def program_assertion(tcds: Tcds) -> ValueAssertion[Program]:
            return asrt_pgm_val.matches_program(
                command=asrt_command.equals_system_program_command(
                    program=the_executable_program,
                    arguments=expected_arguments
                ),
                stdin=asrt_pgm_val.no_stdin(),
                transformer=asrt_line_transformer.is_identity_transformer(True)
            )

        def program_adv_assertion(tcds: Tcds) -> ValueAssertion[ProgramAdv]:
            def get_program(adv: ProgramAdv) -> Program:
                return adv.primitive(application_environment_for_test())

            return asrt.is_instance_with(ProgramAdv,
                                         asrt.sub_component('program',
                                                            get_program,
                                                            program_assertion(tcds)))

        case = ResolvingCase(
            '',
            actual_sdv=program_sdvs.system_program(
                string_sdvs.str_constant(the_executable_program),
                arguments_sdvs.new_without_validation(
                    list_sdvs.from_str_constants(expected_arguments))),
            expected=asrt_dir_dep_val.matches_dir_dependent_value(program_adv_assertion)
        )
        return [case]

    def test(self):
        # ARRANGE #

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
        parser = sut.program_parser()
        for argument_case in argument_cases:
            for program_case in program_cases:
                for resolving_case in program_case.value(argument_case.value):
                    with self.subTest(program=program_case.name,
                                      arguments=argument_case.name,
                                      resolving_case=resolving_case.name):
                        program_symbol = ProgramSymbolContext.of_sdv(
                            'PROGRAM_SYMBOL',
                            resolving_case.actual_sdv)

                        source = parse_source_of(sym_ref_args.sym_ref_cmd_line(program_symbol.name))

                        symbols = program_symbol.symbol_table

                        expected_references_assertion = asrt.matches_sequence([
                            program_symbol.reference_assertion,
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


def parse_source_of(single_line: ArgumentElementsRenderer) -> ParseSource:
    return ArgumentElements([single_line]).as_remaining_source


_INTEGRATION_CHECKER = IntegrationChecker(
    sut.program_parser(),
    program_checker.ProgramPropertiesConfiguration(
        program_checker.ExecutionApplier()
    )
)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
