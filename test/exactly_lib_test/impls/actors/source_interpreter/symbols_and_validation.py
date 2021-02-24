import pathlib
import sys
import unittest

from exactly_lib.impls.actors.source_interpreter import actor as sut
from exactly_lib.impls.types.program.command import command_sdvs, arguments_sdvs
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib_test.impls.actors.file_interpreter.configuration import COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE
from exactly_lib_test.impls.actors.test_resources import relativity_configurations, integration_check
from exactly_lib_test.impls.actors.test_resources.integration_check import Arrangement, Expectation, \
    check_execution, PostSdsExpectation, arrangement_w_tcds
from exactly_lib_test.impls.actors.test_resources.validation_cases import VALIDATION_CASES
from exactly_lib_test.impls.test_resources.validation.svh_validation import ValidationExpectationSvh
from exactly_lib_test.tcfs.test_resources import hds_populators
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as str_asrt
from exactly_lib_test.type_val_deps.types.path.test_resources.path import ConstantSuffixPathDdvSymbolContext, \
    PathSymbolContext
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([

        TestValidationShouldFailWhenInterpreterProgramFileDoesNotExist(),
        TestValidationShouldFailWhenInterpreterProgramFileIsADirectory(),
        TestValidationOfInterpreterArguments(),

        TestStringSymbolReferenceInInterpreter(),
        TestThatSymbolReferencesAreReportedAndUsed(),
        TestThatSourceCanReferenceSymbolsThatAreResolvedPostSds(),
    ])


class TestCaseWInterpreterThatRunsPythonProgramFileBase(unittest.TestCase):
    def _check(self,
               source_line: str,
               arrangement: Arrangement,
               expectation: Expectation):
        check_execution(self,
                        sut.actor(COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE),
                        [instr([source_line])],
                        arrangement,
                        expectation)


class TestThatSymbolReferencesAreReportedAndUsed(TestCaseWInterpreterThatRunsPythonProgramFileBase):
    def runTest(self):
        symbol = StringConstantSymbolContext('symbol_name', 'the symbol value')

        program_that_prints_value_of_symbol = 'print("{symbol}")'

        single_source_line = program_that_prints_value_of_symbol.format(
            symbol=symbol.name__sym_ref_syntax,
        )

        expected_output = symbol.str_value + '\n'

        self._check(
            single_source_line,
            arrangement_w_tcds(
                symbol_table=symbol.symbol_table
            ),
            Expectation(
                symbol_usages=asrt.matches_sequence([
                    symbol.reference_assertion__w_str_rendering,
                ]),
                post_sds=PostSdsExpectation.constant(
                    sub_process_result_from_execute=asrt_pr.stdout(asrt.Equals(expected_output,
                                                                               'program output'))
                ),
            ))


class TestThatSourceCanReferenceSymbolsThatAreResolvedPostSds(TestCaseWInterpreterThatRunsPythonProgramFileBase):
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
            arrangement_w_tcds(
                symbol_table=symbol.symbol_table

            ),
            Expectation(
                symbol_usages=asrt.matches_singleton_sequence(symbol.reference_assertion__w_str_rendering),
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
                path_ddvs.absolute_path(pathlib.Path(sys.executable))
            )
        )

        interpreter_with_symbol_reference = command_sdvs.for_executable_file(
            python_interpreter_symbol.reference_sdv__path_or_string(
                relativity_configurations.INTERPRETER_FILE.relativity
            )
        )

        arrangement = arrangement_w_tcds(
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
                path_ddvs.rel_hds(relativity_configurations.INTERPRETER_FILE.relativity_option_rel_hds,
                                  path_ddvs.constant_path_part('non-existing'))),
        )

        arrangement = arrangement_w_tcds(
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([source_file])
            )
        )

        expectation = Expectation(
            validation=ValidationExpectationSvh.fails__pre_sds()
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
                path_ddvs.rel_hds(relativity_configurations.INTERPRETER_FILE.relativity_option_rel_hds,
                                  path_ddvs.constant_path_part(a_dir.name))),
        )

        arrangement = arrangement_w_tcds(
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
            validation=ValidationExpectationSvh.fails__pre_sds()
        )
        # ACT & ASSERT #
        check_execution(self,
                        sut.actor(interpreter_with_program_that_is_a_dir),
                        [instr([source_file.name])],
                        arrangement,
                        expectation)


class TestValidationOfInterpreterArguments(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for case in VALIDATION_CASES:
            with self.subTest(case.name):
                interpreter_arguments = arguments_sdvs.ref_to_path_that_must_exist(
                    path_sdvs.of_rel_option_with_const_file_name(case.path_relativity,
                                                                 'non-existing-file')
                )
                actor = sut.actor(
                    command_sdvs.for_executable_file(
                        path_sdvs.constant(path_ddvs.absolute_file_name(sys.executable)),
                        interpreter_arguments
                    )
                )
                act_instruction = instr([])
                # ACT & ASSERT #
                integration_check.check_execution(
                    self,
                    actor,
                    [act_instruction],
                    arrangement_w_tcds(),
                    Expectation(validation=case.expectation),
                )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
