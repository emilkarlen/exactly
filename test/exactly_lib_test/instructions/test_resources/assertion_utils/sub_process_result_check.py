import unittest

from exactly_lib.util.process_execution import sub_process_execution as spe
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class IsSuccess(ValueAssertion[spe.ResultAndStderr]):
    def apply(self,
              put: unittest.TestCase,
              value: spe.ResultAndStderr,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, spe.ResultAndStderr)
        put.assertTrue(value.result.is_success,
                       message_builder.apply('Result is expected to indicate success'))


class IsFailure(ValueAssertion[spe.ResultAndStderr]):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, spe.ResultAndStderr)
        put.assertFalse(value.result.is_success,
                        message_builder.apply('Result is expected to indicate failure'))


class ExitCodeIs(ValueAssertion[spe.ResultAndStderr]):
    def __init__(self,
                 exit_code: int):
        self.exit_code = exit_code

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, spe.ResultAndStderr)
        put.assertEqual(self.exit_code,
                        value.result.exit_code,
                        message_builder.apply('Exit code'))


class StderrContentsIs(ValueAssertion[spe.ResultAndStderr]):
    def __init__(self,
                 stderr_contents: str):
        self.stderr_contents = stderr_contents

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, spe.ResultAndStderr)
        put.assertEqual(self.stderr_contents,
                        value.stderr_contents,
                        message_builder.apply('Stderr contents'))


def is_success_result(exitcode: int,
                      stderr_contents: str) -> ValueAssertion[spe.ResultAndStderr]:
    return asrt.and_([IsSuccess(),
                      ExitCodeIs(exitcode),
                      StderrContentsIs(stderr_contents)
                      ])
