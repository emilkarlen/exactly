import unittest
from typing import List

from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output import \
    arguments_building as args, configuration
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.symbol.test_resources import lines_transformer as asrt_transformer
from exactly_lib_test.test_case_utils.external_program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.lines_transformers.test_resources import \
    test_transformers_setup as transformers_setup
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(conf: configuration.ChannelConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestOutputIsEmpty(conf),
        TestOutputIsNotEmpty(conf),
        TestOutputIsEmptyAfterTransformation(conf),
    ])


class TestCaseBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: configuration.ChannelConfiguration):
        super().__init__(configuration)
        self.configuration = configuration

    def _check(self,
               arguments: ArgumentElements,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        instruction_check.check(
            self,
            self.configuration.parser(),
            arguments.as_remaining_source,
            arrangement,
            expectation)

    def _check_positive_and_negated(
            self,
            expectation_of_positive: ExpectationTypeConfig,
            program: ArgumentElements,
            contents_matcher: List,
            expectation_without_main_result_assertion: Expectation,
            arrangement: ArrangementPostAct = ArrangementPostAct()):
        expectation = expectation_without_main_result_assertion

        for case in expectation_of_positive.cases():
            matcher_for_case = args.matcher_for_expectation_type(case.expectation_type, contents_matcher)
            arguments = args.from_program(program, matcher_for_case)

            expectation.main_result = case.main_result_assertion

            with self.subTest(case.expectation_type):
                self._check(
                    arguments,
                    arrangement,
                    expectation)


class TestOutputIsEmpty(TestCaseBase):
    def runTest(self):
        program_that_outputs_nothing = pgm_args.program_elements(
            pgm_args.interpret_py_source_line(self.configuration.py_source_for_print(''))
        )
        result_when_positive = ExpectationTypeConfig(ExpectationType.POSITIVE)

        self._check_positive_and_negated(
            result_when_positive,
            program_that_outputs_nothing,
            args.emptiness_matcher(),
            Expectation())


class TestOutputIsEmptyAfterTransformation(TestCaseBase):
    def runTest(self):
        program_that_outputs_something = pgm_args.program_elements(
            pgm_args.interpret_py_source_line(
                self.configuration.py_source_for_print('some output')),
            transformation=transformers_setup.DELETE_EVERYTHING_TRANSFORMER.name
        )
        result_when_positive = ExpectationTypeConfig(ExpectationType.POSITIVE)

        self._check_positive_and_negated(
            result_when_positive,
            program_that_outputs_something,
            args.emptiness_matcher(),
            Expectation(
                symbol_usages=asrt.matches_sequence([
                    asrt_transformer.is_lines_transformer_reference_to(
                        transformers_setup.DELETE_EVERYTHING_TRANSFORMER.name),
                ])
            ),
            ArrangementPostAct(
                symbols=transformers_setup.SYMBOL_TABLE))


class TestOutputIsNotEmpty(TestCaseBase):
    def runTest(self):
        program_that_outputs_something = pgm_args.program_elements(
            pgm_args.interpret_py_source_line(
                self.configuration.py_source_for_print('some output'))
        )

        result_when_positive = ExpectationTypeConfig(ExpectationType.NEGATIVE)

        self._check_positive_and_negated(
            result_when_positive,
            program_that_outputs_something,
            args.emptiness_matcher(),
            Expectation())
