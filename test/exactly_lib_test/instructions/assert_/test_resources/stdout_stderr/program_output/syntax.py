import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_for_single_section import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.instructions.assert_.test_resources.file_contents import matcher_arguments
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output import \
    arguments_building as po_ab
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output import \
    configuration
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output.configuration import \
    TestCaseBase
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args


def suite_for(conf: configuration.ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestFailingParseDueToMissingProgram(conf),
        TestFailingParseDueToMissingContentsMatcher(conf),
    ])


class TestFailingParseDueToMissingProgram(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        empty_program = ArgumentElements([])
        arguments = po_ab.from_program(empty_program,
                                       matcher_arguments.emptiness_matcher())
        source = arguments.as_remaining_source
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            # ACT #
            self.configuration.parser().parse(source)


class TestFailingParseDueToMissingContentsMatcher(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        program = pgm_args.program(
            pgm_args.interpret_py_source_line('exit(0)')
        )
        no_matcher = []
        arguments = po_ab.from_program(program,
                                       no_matcher)

        source = arguments.as_remaining_source
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            # ACT #
            self.configuration.parser().parse(source)
