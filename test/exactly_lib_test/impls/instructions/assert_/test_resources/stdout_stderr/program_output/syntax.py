import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.impls.instructions.assert_.test_resources.stdout_stderr.program_output import \
    arguments_building as po_ab
from exactly_lib_test.impls.instructions.assert_.test_resources.stdout_stderr.program_output import \
    configuration
from exactly_lib_test.impls.instructions.assert_.test_resources.stdout_stderr.program_output.configuration import \
    TestCaseBase
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.impls.types.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.impls.types.string_matcher.test_resources import matcher_arguments
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO


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
            self.configuration.parser().parse(ARBITRARY_FS_LOCATION_INFO, source)


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
            self.configuration.parser().parse(ARBITRARY_FS_LOCATION_INFO, source)
