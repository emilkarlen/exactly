import unittest

from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.impls.instructions.assert_.process_output.stdout_err.test_resources.program_output import \
    configuration
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.types.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.impls.types.string_matcher.test_resources import matcher_arguments
from exactly_lib_test.impls.types.string_transformer.test_resources import \
    test_transformers_setup as transformers_setup
from exactly_lib_test.impls.types.test_resources import arguments_building as ab
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    pfh_expectation_type_config
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.assertions import \
    is_reference_to_string_transformer__usage


def suite_for(conf: configuration.ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestWithoutTransformation(conf),
        TestWithTransformationFromProgram(conf),
        TestWithTransformationFromProgramAndInstruction(conf),
    ])


class TestWithoutTransformation(configuration.TestCaseBase):
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
            lambda main_result: Expectation(main_result=main_result))


class TestWithTransformationFromProgram(configuration.TestCaseBase):
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
            lambda main_result: Expectation(
                main_result=main_result,
                symbol_usages=asrt.matches_sequence([
                    is_reference_to_string_transformer__usage(transformers_setup.DELETE_INITIAL_WORD_TRANSFORMER.name),
                ])
            ),
            ArrangementPostAct(
                symbols=transformers_setup.SYMBOL_TABLE))


class TestWithTransformationFromProgramAndInstruction(configuration.TestCaseBase):
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
            lambda main_result: Expectation(
                main_result=main_result,
                symbol_usages=asrt.matches_sequence([
                    is_reference_to_string_transformer__usage(transformer_of_program.name),
                    is_reference_to_string_transformer__usage(transformer_of_instruction.name),
                ])
            ),
            arrangement=ArrangementPostAct(
                symbols=transformers_setup.SYMBOL_TABLE),
            transformation=transformer_of_instruction.name
        )
