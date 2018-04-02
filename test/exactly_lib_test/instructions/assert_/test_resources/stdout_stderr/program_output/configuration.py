from typing import List

from exactly_lib.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionParser
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents import matcher_arguments
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output import arguments_building as args
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_resources.arguments_building import Stringable
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class ProgramOutputInstructionConfiguration:
    def parser(self) -> AssertPhaseInstructionParser:
        raise NotImplementedError('abstract method')

    def py_source_for_print(self, output: str) -> str:
        raise NotImplementedError('abstract method')


class TestCaseBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: ProgramOutputInstructionConfiguration):
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
            contents_matcher: List[Stringable],
            expectation_without_main_result_assertion: Expectation,
            arrangement: ArrangementPostAct = ArrangementPostAct(),
            transformation: Stringable = None):
        expectation = expectation_without_main_result_assertion

        for case in expectation_of_positive.cases():
            matcher_for_case = matcher_arguments.matcher_for_expectation_type(case.expectation_type, contents_matcher)
            arguments = args.from_program(program, matcher_for_case, transformation)

            expectation.main_result = case.main_result_assertion

            with self.subTest(case.expectation_type):
                self._check(
                    arguments,
                    arrangement,
                    expectation)