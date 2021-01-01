import unittest

from exactly_lib_test.impls.instructions.assert_.test_resources.stdout_stderr.program_output import \
    symbols_usages_and_validation, empty, transformations, syntax, execute_program_once
from exactly_lib_test.impls.instructions.assert_.test_resources.stdout_stderr.program_output.configuration import \
    ProgramOutputInstructionConfiguration


def suite_for(conf: ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        syntax.suite_for(conf),
        symbols_usages_and_validation.suite_for(conf),
        empty.suite_for(conf),
        transformations.suite_for(conf),
        execute_program_once.suite_for(conf),
    ])
