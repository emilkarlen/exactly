import pathlib
import sys
import unittest

from exactly_lib.actors.source_interpreter import actor as sut
from exactly_lib.symbol.data import path_sdvs
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.program.command import command_sdvs
from exactly_lib.type_system.data import paths
from exactly_lib_test.actors.test_resources import relativity_configurations
from exactly_lib_test.actors.test_resources.integration_check import Arrangement, Expectation, \
    check_execution, PostSdsExpectation
from exactly_lib_test.symbol.data.test_resources.path import ConstantSuffixPathDdvSymbolContext, PathSymbolContext
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators
from exactly_lib_test.test_case_utils.test_resources.validation import pre_sds_validation_fails__svh
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as str_asrt


def suite_for(parser_that_executes_python_program: Actor) -> unittest.TestSuite:
    return unittest.TestSuite([

        TestValidationShouldFailWhenInterpreterProgramFileDoesNotExist(),
        TestValidationShouldFailWhenInterpreterProgramFileIsADirectory(),

        TestStringSymbolReferenceInInterpreter(),
        TestThatSymbolReferencesAreReportedAndUsed(parser_that_executes_python_program),
        TestThatSourceCanReferenceSymbolsThatAreResolvedPostSds(parser_that_executes_python_program),
    ])


class TestCaseBase(unittest.TestCase):
    def __init__(self,
                 actor_that_executes_python_program: Actor,
                 ):
        super().__init__()
        self.actor_that_executes_python_program = actor_that_executes_python_program

    def shortDescription(self):
        return str(type(self))

    def _check(self,
               source_line: str,
               arrangement: Arrangement,
               expectation: Expectation):
        check_execution(self,
                        self.actor_that_executes_python_program,
                        [instr([source_line])],
                        arrangement,
                        expectation)


class TestThatSymbolReferencesAreReportedAndUsed(TestCaseBase):
    def runTest(self):
        symbol = StringConstantSymbolContext('symbol_name', 'the symbol value')

        program_that_prints_value_of_symbol = 'print("{symbol}")'

        single_source_line = program_that_prints_value_of_symbol.format(
            symbol=symbol.name__sym_ref_syntax,
        )

        expected_output = symbol.str_value + '\n'

        self._check(
            single_source_line,
            Arrangement(
                symbol_table=symbol.symbol_table
            ),
            Expectation(
                symbol_usages=asrt.matches_sequence([
                    symbol.reference_assertion__any_data_type,
                ]),
                post_sds=PostSdsExpectation.constant(
                    sub_process_result_from_execute=asrt_pr.stdout(asrt.Equals(expected_output,
                                                                               'program output'))
                ),
            ))


class TestThatSourceCanReferenceSymbolsThatAreResolvedPostSds(TestCaseBase):
    def runTest(self):
        symbol = ConstantSuffixPathDdvSymbolContext('symbol_name',
                                                    RelOptionType.REL_ACT,
                                                    'the-path-suffix')

        program_that_prints_value_of_symbol = 'print("{symbol}")'

        single_source_line = program_that_prints_value_of_symbol.format(
            symbol=symbol.name__sym_ref_syntax,
        )

        self._check(
            single_source_line,
            Arrangement(
                symbol_table=symbol.symbol_table

            ),
            Expectation(
                symbol_usages=asrt.matches_singleton_sequence(symbol.reference_assertion__any_data_type),
                post_sds=PostSdsExpectation.constant(
                    sub_process_result_from_execute=asrt_pr.stdout(str_asrt.contains(symbol.path_suffix))
                ),
            ))


class TestStringSymbolReferenceInInterpreter(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        source_file = fs.File.empty('source-file.src')

        python_interpreter_symbol = PathSymbolContext.of_sdv(
            'PYTHON_INTERPRETER_SYMBOL',
            path_sdvs.constant(
                paths.absolute_path(pathlib.Path(sys.executable))
            )
        )

        interpreter_with_symbol_reference = command_sdvs.for_executable_file(
            python_interpreter_symbol.reference_sdv__path_or_string(
                relativity_configurations.INTERPRETER_FILE.relativity
            )
        )

        arrangement = Arrangement(
            symbol_table=python_interpreter_symbol.symbol_table,
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([source_file])
            )
        )
        expectation = Expectation(
            symbol_usages=asrt.matches_singleton_sequence(
                python_interpreter_symbol.reference_assertion__path_or_string),
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=asrt_pr.sub_process_result(
                    exitcode=asrt.equals(0),
                    stdout=asrt.equals(''),
                    stderr=asrt.equals(''),
                )
            ),
        )
        # ACT & ASSERT #
        check_execution(self,
                        sut.actor(interpreter_with_symbol_reference),
                        [instr([])],
                        arrangement,
                        expectation)


class TestValidationShouldFailWhenInterpreterProgramFileDoesNotExist(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        source_file = fs.File.empty('source-file.src')

        interpreter_with_non_existing_program_file = command_sdvs.for_executable_file(
            path_sdvs.constant(
                paths.rel_hds(relativity_configurations.INTERPRETER_FILE.relativity_option_rel_hds,
                              paths.constant_path_part('non-existing'))),
        )

        arrangement = Arrangement(
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([source_file])
            )
        )

        expectation = Expectation(
            validation=pre_sds_validation_fails__svh()
        )
        # ACT & ASSERT #
        check_execution(self,
                        sut.actor(interpreter_with_non_existing_program_file),
                        [instr([source_file.name])],
                        arrangement,
                        expectation)


class TestValidationShouldFailWhenInterpreterProgramFileIsADirectory(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        source_file = fs.File.empty('source-file.src')
        a_dir = fs.Dir.empty('a-dir')

        interpreter_with_program_that_is_a_dir = command_sdvs.for_executable_file(
            path_sdvs.constant(
                paths.rel_hds(relativity_configurations.INTERPRETER_FILE.relativity_option_rel_hds,
                              paths.constant_path_part(a_dir.name))),
        )

        arrangement = Arrangement(
            hds_contents=hds_populators.multiple([
                relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                    fs.DirContents([source_file])
                ),
                relativity_configurations.INTERPRETER_FILE.populator_for_relativity_option_root__hds(
                    fs.DirContents([a_dir])
                ),
            ])
        )
        expectation = Expectation(
            validation=pre_sds_validation_fails__svh()
        )
        # ACT & ASSERT #
        check_execution(self,
                        sut.actor(interpreter_with_program_that_is_a_dir),
                        [instr([source_file.name])],
                        arrangement,
                        expectation)
