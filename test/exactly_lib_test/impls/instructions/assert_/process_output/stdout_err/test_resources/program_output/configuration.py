from typing import List

from exactly_lib.impls.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionParser
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.instructions.assert_.process_output.stdout_err.test_resources.program_output import \
    arguments_building as args
from exactly_lib_test.impls.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.impls.types.string_matcher.test_resources import matcher_arguments
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForPfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.strings import WithToString
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class ProgramOutputInstructionConfiguration:
    def parser(self) -> AssertPhaseInstructionParser:
        raise NotImplementedError('abstract method')

    def output_file(self) -> ProcOutputFile:
        raise NotImplementedError('abstract method')

    def py_source_for_print(self, output: str) -> str:
        return py_programs.single_line_pgm_that_prints_to(self.output_file(), output)


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
            expectation_of_positive: ExpectationTypeConfigForPfh,
            program: ArgumentElements,
            contents_matcher: List[WithToString],
            expectation_without_main_result_assertion: Expectation,
            arrangement: ArrangementPostAct = ArrangementPostAct(),
            transformation: WithToString = None):
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
