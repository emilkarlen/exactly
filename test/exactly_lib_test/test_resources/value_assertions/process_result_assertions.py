import unittest

from exactly_lib.common.exit_value import ExitValue
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as asrt_str
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase


def is_result_for_exit_value(expected: ExitValue) -> Assertion[SubProcessResult]:
    return SubProcessExitValueAssertion(expected)


def matches_proc_result(
        exit_code: Assertion[int] = asrt.anything_goes(),
        stdout: Assertion[str] = asrt.anything_goes(),
        stderr: Assertion[str] = asrt.anything_goes(),
) -> Assertion[SubProcessResult]:
    return asrt.is_instance_with__many(
        SubProcessResult,
        [
            asrt.sub_component(
                'exit_code',
                SubProcessResult.exitcode.fget,
                exit_code,
            ),
            asrt.sub_component(
                'stdout',
                SubProcessResult.stdout.fget,
                stdout,
            ),
            asrt.sub_component(
                'stderr',
                SubProcessResult.stderr.fget,
                stderr,
            ),
        ]
    )


def is_result_for_exit_value_on_stderr_and_empty_stdout(expected: ExitValue,
                                                        contents_after_exit_value_allowed: bool = False
                                                        ) -> Assertion[SubProcessResult]:
    exit_value_string = expected.exit_identifier + '\n'
    stderr_expectation = (
        asrt_str.begins_with(exit_value_string)
        if contents_after_exit_value_allowed
        else
        asrt.equals(exit_value_string)
    )
    return sub_process_result(exitcode=asrt.equals(expected.exit_code),
                              stderr=stderr_expectation,
                              stdout=asrt.equals(''))


def is_result_for_failure_exit_value_on_stderr(expected: ExitValue) -> Assertion[SubProcessResult]:
    return SubProcessExitValueOnStdErrAssertion(expected)


def is_result_for_exit_code(exit_code: int) -> Assertion[SubProcessResult]:
    return _SubProcessResultAssertion(exitcode=asrt.equals(exit_code))


def is_result_for_empty_stdout(exit_code: int) -> Assertion[SubProcessResult]:
    return _SubProcessResultAssertion(exitcode=asrt.equals(exit_code),
                                      stdout=asrt.equals(''))


def is_result_for_empty_stderr(exit_code: int) -> Assertion[SubProcessResult]:
    return _SubProcessResultAssertion(exitcode=asrt.equals(exit_code),
                                      stderr=asrt.equals(''))


def stdout(assertion_on_str: Assertion[str]) -> Assertion[SubProcessResult]:
    return _SubProcessResultAssertion(stdout=assertion_on_str)


def sub_process_result(exitcode: Assertion[int] = asrt.anything_goes(),
                       stdout: Assertion[str] = asrt.anything_goes(),
                       stderr: Assertion[str] = asrt.anything_goes(),
                       ) -> Assertion[SubProcessResult]:
    return _SubProcessResultAssertion(exitcode,
                                      stdout,
                                      stderr)


class _SubProcessResultAssertion(AssertionBase[SubProcessResult]):
    def __init__(self,
                 exitcode: Assertion[int] = asrt.anything_goes(),
                 stdout: Assertion[str] = asrt.anything_goes(),
                 stderr: Assertion[str] = asrt.anything_goes(),
                 ):
        self._exitcode = exitcode
        self._stdout = stdout
        self._stderr = stderr

    def _apply(self,
               put: unittest.TestCase,
               value: SubProcessResult,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value,
                             SubProcessResult,
                             message_builder.for_sub_component('class of result object').apply(
                                 'Expects ' + str(SubProcessResult)))
        msg_info = _err_msg_info(value)
        self._exitcode.apply(put, value.exitcode,
                             message_builder.for_sub_component('exitcode' + msg_info))

        self._stdout.apply(put, value.stdout,
                           message_builder.for_sub_component('stdout' + msg_info))

        self._stderr.apply(put, value.stderr,
                           message_builder.for_sub_component('stderr' + msg_info))


class SubProcessExitValueAssertion(AssertionBase[SubProcessResult]):
    def __init__(self,
                 expected: ExitValue,
                 message: str = None):
        self.expected = expected
        self.message = message

    def _apply(self,
               put: unittest.TestCase,
               value: SubProcessResult,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value,
                             SubProcessResult,
                             message_builder.for_sub_component('class of result object').apply(
                                 'Expects ' + str(SubProcessResult)))
        msg_info = _err_msg_info(value)
        put.assertEqual(self.expected.exit_code,
                        value.exitcode,
                        message_builder.for_sub_component('exitcode').apply(msg_info))
        put.assertEqual(self.expected.exit_identifier + '\n',
                        value.stdout,
                        message_builder.for_sub_component('exit identifier').apply(msg_info))


class SubProcessExitValueOnStdErrAssertion(AssertionBase[SubProcessResult]):
    def __init__(self,
                 expected: ExitValue,
                 message: str = None):
        self.expected = expected
        self.message = message

    def _apply(self,
               put: unittest.TestCase,
               value: SubProcessResult,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value,
                             SubProcessResult,
                             message_builder.for_sub_component('class of result object').apply(
                                 'Expects ' + str(SubProcessResult)))
        msg_info = _err_msg_info(value)
        put.assertEqual(self.expected.exit_code,
                        value.exitcode,
                        message_builder.for_sub_component('exitcode').apply(msg_info))

        stderr_lines = value.stderr.split('\n')
        first_line_of_stderr = '' if not stderr_lines else stderr_lines[0]
        put.assertEqual(self.expected.exit_identifier,
                        first_line_of_stderr,
                        message_builder.for_sub_component('exit identifier on stderr').apply(msg_info))

        put.assertEqual('',
                        value.stdout,
                        message_builder.for_sub_component('stdout').apply(msg_info))


def _err_msg_info(actual: SubProcessResult) -> str:
    return """
Info from actual value:
exit_code = {exit_code}
stdout    = "{stdout}"
stderr    = "{stderr}\"""".format(
        exit_code=actual.exitcode,
        stdout=actual.stdout,
        stderr=actual.stderr)
