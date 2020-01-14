import unittest

from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output import \
    configuration
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output.configuration import TestCaseBase
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.string_matcher.test_resources import matcher_arguments
from exactly_lib_test.test_case_utils.string_transformers.test_resources import \
    test_transformers_setup as transformers_setup
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    pfh_expectation_type_config
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(conf: configuration.ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestWithoutTransformation(conf),
        TestWithTransformationFromProgram(conf),
        TestWithTransformationFromProgramAndInstruction(conf),
    ])


class TestWithoutTransformation(TestCaseBase):
    def runTest(self):
        output = 'output from program'
        program_that_outputs_nothing = pgm_args.program(
            pgm_args.interpret_py_source_line(self.configuration.py_source_for_print(output))
        )
        result_when_positive = pfh_expectation_type_config(ExpectationType.POSITIVE)

        self._check_positive_and_negated(
            result_when_positive,
            program_that_outputs_nothing,
            matcher_arguments.equals_matcher(ab.quoted_string(output)),
            Expectation())


class TestWithTransformationFromProgram(TestCaseBase):
    def runTest(self):
        output_from_program = 'first second'
        program_that_outputs_something = pgm_args.program(
            pgm_args.interpret_py_source_line(
                self.configuration.py_source_for_print(output_from_program)),
            transformation=transformers_setup.DELETE_INITIAL_WORD_TRANSFORMER.name
        )
        result_when_positive = pfh_expectation_type_config(ExpectationType.POSITIVE)

        self._check_positive_and_negated(
            result_when_positive,
            program_that_outputs_something,
            matcher_arguments.equals_matcher(ab.quoted_string('second')),
            Expectation(
                symbol_usages=asrt.matches_sequence([
                    is_reference_to_string_transformer(transformers_setup.DELETE_INITIAL_WORD_TRANSFORMER.name),
                ])
            ),
            ArrangementPostAct(
                symbols=transformers_setup.SYMBOL_TABLE))


class TestWithTransformationFromProgramAndInstruction(TestCaseBase):
    def runTest(self):
        output_from_program = 'first second'
        transformer_of_program = transformers_setup.DELETE_INITIAL_WORD_TRANSFORMER
        transformer_of_instruction = transformers_setup.DUPLICATE_WORDS_TRANSFORMER

        program_that_outputs_something = pgm_args.program(
            pgm_args.interpret_py_source_line(
                self.configuration.py_source_for_print(output_from_program)),
            transformation=transformer_of_program.name
        )
        result_when_positive = pfh_expectation_type_config(ExpectationType.POSITIVE)

        self._check_positive_and_negated(
            result_when_positive,
            program_that_outputs_something,
            matcher_arguments.equals_matcher(ab.quoted_string('second second')),
            Expectation(
                symbol_usages=asrt.matches_sequence([
                    is_reference_to_string_transformer(transformer_of_program.name),
                    is_reference_to_string_transformer(transformer_of_instruction.name),
                ])
            ),
            arrangement=ArrangementPostAct(
                symbols=transformers_setup.SYMBOL_TABLE),
            transformation=transformer_of_instruction.name
        )
