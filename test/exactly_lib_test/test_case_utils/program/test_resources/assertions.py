import unittest

from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder


class ResultWithTransformationData:
    def __init__(self,
                 process_result: SubProcessResult,
                 result_of_transformation: str):
        self.process_result = process_result
        self.result_of_transformation = result_of_transformation


def assert_process_result_data(exitcode: ValueAssertion[int] = asrt.anything_goes(),
                               stdout_contents: ValueAssertion[str] = asrt.anything_goes(),
                               stderr_contents: ValueAssertion[str] = asrt.anything_goes(),
                               contents_after_transformation: ValueAssertion[str] = asrt.anything_goes(),
                               ) -> ValueAssertion[ResultWithTransformationData]:
    return ResultWithTransformationDataAssertion(exitcode,
                                                 stdout_contents,
                                                 stderr_contents,
                                                 contents_after_transformation)


class ResultWithTransformationDataAssertion(ValueAssertionBase[ResultWithTransformationData]):
    def __init__(self,
                 exitcode: ValueAssertion[int] = asrt.anything_goes(),
                 stdout_contents: ValueAssertion[str] = asrt.anything_goes(),
                 stderr_contents: ValueAssertion[str] = asrt.anything_goes(),
                 contents_after_transformation: ValueAssertion[str] = asrt.anything_goes()
                 ):
        self.exitcode = exitcode
        self.stdout_contents = stdout_contents
        self.stderr_contents = stderr_contents
        self.contents_after_transformation = contents_after_transformation

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: MessageBuilder):
        put.assertIsInstance(value, ResultWithTransformationData,
                             message_builder.apply("result object class"))
        assert isinstance(value, ResultWithTransformationData)  # Type info for IDE
        pr = value.process_result
        self.exitcode.apply(put,
                            pr.exitcode,
                            message_builder.for_sub_component('exitcode'))
        self.stdout_contents.apply(put,
                                   pr.stdout,
                                   message_builder.for_sub_component('stdout'))
        self.stderr_contents.apply(put,
                                   pr.stderr,
                                   message_builder.for_sub_component('stderr'))
        self.contents_after_transformation.apply(put,
                                                 value.result_of_transformation,
                                                 message_builder.for_sub_component('contents_after_transformation'))
