import unittest
from typing import List

from exactly_lib_test.cli.program_modes.symbol.test_resources import cl_arguments as symbol_args
from exactly_lib_test.cli.program_modes.test_resources import test_with_files_in_tmp_dir
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def check_case_and_suite(put: unittest.TestCase,
                         symbol_command_arguments: List[str],
                         arrangement: Arrangement,
                         expectation: ValueAssertion[SubProcessResult]):
    """
    Runs one test with arguments for test-case and one for test-suite.

    Adds (prepends) command line arguments for triggering the "symbol" command.

    :param symbol_command_arguments: Command line arguments except those that specifies the "symbol" command.
    """
    for source_type_case in _SOURCE_TYPE_CASES:
        with put.subTest(source_type=source_type_case.name,
                         arguments=symbol_command_arguments):
            test_with_files_in_tmp_dir.check(put,
                                             source_type_case.value(symbol_command_arguments),
                                             arrangement,
                                             expectation)


_SOURCE_TYPE_CASES = [
    NameAndValue('case',
                 symbol_args.arguments,
                 ),
    NameAndValue('suite',
                 symbol_args.arguments__suite,
                 ),
]
