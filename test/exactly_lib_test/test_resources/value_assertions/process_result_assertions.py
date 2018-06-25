import unittest

from exactly_lib.common.exit_value import ExitValue
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_result_for_exit_value(expected: ExitValue) -> asrt.ValueAssertion[SubProcessResult]:
    return SubProcessExitValueAssertion(expected)


def is_result_for_exit_code(exit_code: int) -> asrt.ValueAssertion[SubProcessResult]:
    return _SubProcessResultAssertion(exitcode=asrt.equals(exit_code))


def is_result_for_empty_stdout(exit_code: int) -> asrt.ValueAssertion[SubProcessResult]:
    return _SubProcessResultAssertion(exitcode=asrt.equals(exit_code),
                                      stdout=asrt.equals(''))


def stdout(assertion_on_str: asrt.ValueAssertion[str]) -> asrt.ValueAssertion[SubProcessResult]:
    return _SubProcessResultAssertion(stdout=assertion_on_str)


def sub_process_result(exitcode: asrt.ValueAssertion = asrt.anything_goes(),
                       stdout: asrt.ValueAssertion = asrt.anything_goes(),
                       stderr: asrt.ValueAssertion = asrt.anything_goes(),
                       ) -> asrt.ValueAssertion[SubProcessResult]:
    return asrt.is_instance_with(SubProcessResult,
                                 asrt.and_([
                                     asrt.sub_component('exitcode',
                                                        SubProcessResult.exitcode.fget,
                                                        exitcode),
                                     asrt.sub_component('stdout',
                                                        SubProcessResult.stdout.fget,
                                                        stdout),
                                     asrt.sub_component('stderr',
                                                        SubProcessResult.stderr.fget,
                                                        stderr),
                                 ]))


class _SubProcessResultAssertion(asrt.ValueAssertion[SubProcessResult]):
    def __init__(self,
                 exitcode: asrt.ValueAssertion = asrt.anything_goes(),
                 stdout: asrt.ValueAssertion = asrt.anything_goes(),
                 stderr: asrt.ValueAssertion = asrt.anything_goes(),
                 ):
        self._exitcode = exitcode
        self._stdout = stdout
        self._stderr = stderr

    def apply(self,
              put: unittest.TestCase,
              value: SubProcessResult,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value,
                             SubProcessResult,
                             message_builder.for_sub_component('class of result object').apply(
                                 'Expects ' + str(SubProcessResult)))
        msg_info = '\nInfo from actual value:\nstdout = "{stdout}"\nstderr="{stderr}"'.format(stdout=value.stdout,
                                                                                              stderr=value.stderr)
        self._exitcode.apply(put, value.exitcode,
                             message_builder.for_sub_component('exitcode' + msg_info))

        self._stdout.apply(put, value.stdout,
                           message_builder.for_sub_component('stdout' + msg_info))

        self._stderr.apply(put, value.stderr,
                           message_builder.for_sub_component('stderr' + msg_info))


class SubProcessExitValueAssertion(asrt.ValueAssertion[SubProcessResult]):
    def __init__(self,
                 expected: ExitValue,
                 message: str = None):
        self.expected = expected
        self.message = message

    def apply(self,
              put: unittest.TestCase,
              value: SubProcessResult,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value,
                             SubProcessResult,
                             message_builder.for_sub_component('class of result object').apply(
                                 'Expects ' + str(SubProcessResult)))
        msg_info = 'Info from actual value:\nstdout = "{stdout}"\nstderr="{stderr}"'.format(stdout=value.stdout,
                                                                                            stderr=value.stderr)
        put.assertEqual(self.expected.exit_code,
                        value.exitcode,
                        message_builder.for_sub_component('exitcode').apply(msg_info))
        put.assertEqual(self.expected.exit_identifier + '\n',
                        value.stdout,
                        message_builder.for_sub_component('exit identifier').apply(msg_info))
