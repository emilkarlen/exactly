import unittest

from exactly_lib.impls.types.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_val_prims.program.commands import system_program_command
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.type_val_prims.program.stdin import StdinData
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.program.test_resources import program_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_matches(self):
        command = system_program_command('program', [])
        stdin_data = StdinData([])
        transformer = IdentityStringTransformer()
        sut.matches_program(
            command=asrt.is_(command),
            stdin=asrt.is_(stdin_data),
            transformer=asrt.is_(transformer),
        )

    def test_not_matches(self):
        expected_command = system_program_command('program', [])
        expected_stdin_data = StdinData([])
        expected_transformer = IdentityStringTransformer()

        assertion = sut.matches_program(
            command=asrt.is_(expected_command),
            stdin=asrt.is_(expected_stdin_data),
            transformer=asrt.is_(expected_transformer),
        )

        actual_command = system_program_command('program', [])
        actual_stdin_data = StdinData([])
        actual_transformer = IdentityStringTransformer()

        cases = [
            NameAndValue('unexpected command',
                         Program(
                             command=actual_command,
                             stdin=expected_stdin_data,
                             transformation=expected_transformer
                         )
                         ),
            NameAndValue('unexpected stdin',
                         Program(
                             command=expected_command,
                             stdin=actual_stdin_data,
                             transformation=expected_transformer
                         )
                         ),
            NameAndValue('unexpected transformer',
                         Program(
                             command=expected_command,
                             stdin=expected_stdin_data,
                             transformation=actual_transformer
                         )
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(assertion, case.value)
