import unittest

from exactly_lib_test.impls.instructions.assert_.stdout_err.test_resources.program_output import \
    symbols_usages_and_validation, empty, transformations, execute_program_once, stdin
from exactly_lib_test.impls.instructions.assert_.stdout_err.test_resources.program_output import syntax
from exactly_lib_test.impls.instructions.assert_.stdout_err.test_resources.program_output.configuration import \
    ProgramOutputInstructionConfiguration


def suite_for(conf: ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        syntax.suite_for(conf),
        symbols_usages_and_validation.suite_for(conf),
        empty.suite_for(conf),
        transformations.suite_for(conf),
        stdin.suite_for(conf),
        execute_program_once.suite_for(conf),
    ])
