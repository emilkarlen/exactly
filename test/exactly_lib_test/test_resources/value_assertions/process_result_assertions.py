import os
import unittest

from exactly_lib.common.exit_value import ExitValue
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_result_for_exit_value(expected: ExitValue) -> asrt.ValueAssertion:
    """
    :rtype: A ValueAssertion on a SubProcessResult.
    """
    return SubProcessExitValueAssertion(expected)


def is_result_for_exit_code(exit_code: int) -> asrt.ValueAssertion:
    """
    :rtype: A ValueAssertion on a SubProcessResult.
    """
    return asrt.sub_component('exit code',
                              SubProcessResult.exitcode.fget,
                              asrt.Equals(exit_code))


def stdout(assertion_on_str: asrt.ValueAssertion) -> asrt.ValueAssertion:
    """
    :type assertion_on_str: An assertion on a str.
    :rtype: A ValueAssertion on a SubProcessResult.
    """
    return asrt.sub_component('stdout',
                              SubProcessResult.stdout.fget,
                              assertion_on_str)


def sub_process_result(exitcode: asrt.ValueAssertion = asrt.anything_goes(),
                       stdout: asrt.ValueAssertion = asrt.anything_goes(),
                       stderr: asrt.ValueAssertion = asrt.anything_goes(),
                       ) -> asrt.ValueAssertion:
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


class SubProcessExitValueAssertion(asrt.ValueAssertion):
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
        put.assertEqual(self.expected.exit_identifier + os.linesep,
                        value.stdout,
                        message_builder.for_sub_component('exit identifier').apply(msg_info))
