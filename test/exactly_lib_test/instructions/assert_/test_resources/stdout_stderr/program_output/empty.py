import unittest

from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources.file_contents import matcher_arguments
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output import \
    configuration
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output.configuration import \
    TestCaseBase
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.symbol.test_resources.lines_transformer import is_reference_to_lines_transformer
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import \
    test_transformers_setup as transformers_setup
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(conf: configuration.ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestOutputIsEmpty(conf),
        TestOutputIsNotEmpty(conf),
        TestOutputIsEmptyAfterTransformation(conf),
    ])


class TestOutputIsEmpty(TestCaseBase):
    def runTest(self):
        program_that_outputs_nothing = pgm_args.program(
            pgm_args.interpret_py_source_line(self.configuration.py_source_for_print(''))
        )
        result_when_positive = ExpectationTypeConfig(ExpectationType.POSITIVE)

        self._check_positive_and_negated(
            result_when_positive,
            program_that_outputs_nothing,
            matcher_arguments.emptiness_matcher(),
            Expectation())


class TestOutputIsEmptyAfterTransformation(TestCaseBase):
    def runTest(self):
        program_that_outputs_something = pgm_args.program(
            pgm_args.interpret_py_source_line(
                self.configuration.py_source_for_print('some output')),
            transformation=transformers_setup.DELETE_EVERYTHING_TRANSFORMER.name
        )
        result_when_positive = ExpectationTypeConfig(ExpectationType.POSITIVE)

        self._check_positive_and_negated(
            result_when_positive,
            program_that_outputs_something,
            matcher_arguments.emptiness_matcher(),
            Expectation(
                symbol_usages=asrt.matches_sequence([
                    is_reference_to_lines_transformer(transformers_setup.DELETE_EVERYTHING_TRANSFORMER.name),
                ])
            ),
            ArrangementPostAct(
                symbols=transformers_setup.SYMBOL_TABLE))


class TestOutputIsNotEmpty(TestCaseBase):
    def runTest(self):
        program_that_outputs_something = pgm_args.program(
            pgm_args.interpret_py_source_line(
                self.configuration.py_source_for_print('some output'))
        )

        result_when_positive = ExpectationTypeConfig(ExpectationType.NEGATIVE)

        self._check_positive_and_negated(
            result_when_positive,
            program_that_outputs_something,
            matcher_arguments.emptiness_matcher(),
            Expectation())
